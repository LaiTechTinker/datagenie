"""Mocked LLM report generation + chat. Swap to a real LLM by replacing _generate()."""
import random
import re
import uuid
import time
import pandas as pd
from utils.profilling import profile_data,profile_to_text
from utils.LLM import generate_insights,init_llm
from langchain_core.prompts import PromptTemplate
from utils.prompts import chat_prompt
from models import dataset as ds_model
from models import report as report_model
from utils.pdf_prev import generate_pdf_report
from utils.errors import ApiError
from utils.S3 import download_pdf_from_s3, upload_pdf_to_s3, generate_presigned_url


def _split_insights_to_bullets(insights_text: str) -> list[str]:
    """Best-effort conversion of an LLM string into bullet-like lines."""
    if not insights_text:
        return []

    # Split by newlines first.
    lines = [l.strip() for l in insights_text.split("\n") if l.strip()]
    # If it looks like a single paragraph, also split on sentence boundaries.
    if len(lines) <= 1:
        sentences = re.split(r"(?<=[.!?])\s+", insights_text.strip())
        lines = [s.strip() for s in sentences if s.strip()]

    # Remove common bullet prefixes.
    cleaned: list[str] = []
    for l in lines:
        cleaned.append(re.sub(r"^[-*•]\s*", "", l).strip())

    return cleaned


def _extract_summary(summary_text: str, bullets: list[str]) -> str:
    if summary_text and summary_text.strip():
        # Use first paragraph / line.
        first_line = summary_text.strip().split("\n")[0].strip()
        return first_line[:500]
    return (bullets[0] if bullets else "")[:500]


def _generate(dataset: dict) -> dict:

    rows = dataset.get("rows", [])
    df = pd.DataFrame(rows)
    profile = profile_data(df)
    profile_text = profile_to_text(profile)

    insights_text = generate_insights(profile_text)
    bullets = _split_insights_to_bullets(insights_text)
    summary = _extract_summary("", bullets)

    # Best-effort issues extraction from the same text (can be empty).
    issues: list[str] = []
    for b in bullets:
        if re.search(r"missing|null|duplicate|outlier|error|issue|problem|quality", b, re.I):
            issues.append(b)
    if not issues:
        issues = ["No major data quality issues detected."]

    # Build a structured text block for the PDF generator.
    pdf_text = "\n".join(
        [
            "INSIGHTS REPORT",
            "",
            f"SUMMARY: {summary}",
            "",
            "KEY INSIGHTS",
            *(f"- {b}" for b in bullets[:30]),
            "",
            "DATA ISSUES",
            *(f"- {i}" for i in issues[:20]),
        ]
    )

    report_file_id = str(uuid.uuid4())
    s3_key = generate_pdf_report(pdf_text, report_file_id)

    return {
        "summary": summary,
        "insights": bullets,
        "issues": issues,
        "file_path": s3_key,
        "file_id": report_file_id,
    }



def generate_for_dataset(user_id: str, dataset_id: str) -> dict:
    d = ds_model.get(user_id, dataset_id)
    if not d:
        raise ApiError("Dataset not found", 404)

    payload = _generate(d)
    rep = report_model.create(
        dataset_id,
        payload["file_path"],
        payload["insights"],
        payload["file_id"],
        summary=payload.get("summary"),
        issues=payload.get("issues"),
    )
    return report_model.serialize(rep)





def get(report_id: str) -> dict:
    r = report_model.get(report_id)
    if not r:
        raise ApiError("Report not found", 404)
    return report_model.serialize(r)


def _ensure_report_belongs_to_user(user_id: str, report_id: str) -> dict:
    r = report_model.get(report_id)
    if not r:
        raise ApiError("Report not found", 404)
    if not ds_model.get(user_id, r.get("dataset_id")):
        raise ApiError("Report not found", 404)
    return r


def get_pdf_for_report(user_id: str, report_id: str) -> tuple[bytes, str]:
    r = _ensure_report_belongs_to_user(user_id, report_id)
    s3_key = r.get("file_path")

    if isinstance(s3_key, str) and s3_key.strip():
        try:
            pdf_bytes = download_pdf_from_s3(s3_key)
            return pdf_bytes, f"report_{report_id}.pdf"
        except RuntimeError:
            # If S3 object is missing or cannot be read, regenerate it.
            pass

    summary = r.get("summary", "") or ""
    insights = r.get("insights", []) or []
    issues = r.get("issues", []) or []

    pdf_text = "\n".join(
        [
            "INSIGHTS REPORT",
            "",
            f"SUMMARY: {summary}",
            "",
            "KEY INSIGHTS",
            *(f"- {b}" for b in insights[:30]),
            "",
            "DATA ISSUES",
            *(f"- {i}" for i in issues[:20]),
        ]
    )

    s3_key = generate_pdf_report(pdf_text, report_id)
    report_model.update_file_path(report_id, s3_key)
    pdf_bytes = download_pdf_from_s3(s3_key)
    return pdf_bytes, f"report_{report_id}.pdf"


_CANNED = [
    "Based on the report, the dataset is well-suited for a baseline model.",
    "Consider handling missing values before training to improve accuracy.",
    "The most predictive features are likely the numeric columns with low variance loss.",
    "A tree-based model is a strong starting point for tabular data of this shape.",
]

def send_pdf_file(report_id: str):
    r = report_model.get(report_id)
    if not r:
        raise ApiError("Report not found for this user", 404)

    s3_key = r.get("file_path")
    if isinstance(s3_key, str) and s3_key.strip():
        return generate_presigned_url(s3_key)

    summary = r.get("summary", "") or ""
    insights = r.get("insights", []) or []
    issues = r.get("issues", []) or []

    pdf_text = "\n".join(
        [
            "INSIGHTS REPORT",
            "",
            f"SUMMARY: {summary}",
            "",
            "KEY INSIGHTS",
            *(f"- {b}" for b in insights[:30]),
            "",
            "DATA ISSUES",
            *(f"- {i}" for i in issues[:20]),
        ]
    )

    s3_key = generate_pdf_report(pdf_text, report_id)
    report_model.update_file_path(report_id, s3_key)

    return generate_presigned_url(s3_key)


def format_memory(memory_list):
    formatted = ""
    for msg in memory_list:
        role = "User" if msg["role"] == "user" else "assistant"
        formatted += f"{role}: {msg['content']}\\n"
    return formatted


def chat(report_id: str, message: str) -> dict:
    """Grounded chat using per-report memory stored in `report.chat`.

    Prevents hallucination by instructing the LLM to answer only from the stored
    report fields + conversation history.
    """
    if not message or not message.strip():
        raise ApiError("Message cannot be empty", 400)

    r = report_model.get(report_id)
    if not r:
        raise ApiError("Report not found for this user", 404)

    # Use stored report fields as the only knowledge source.
    summary = r.get("summary", "") or ""
    insights_list = r.get("insights", []) or []
    issues_list = r.get("issues", []) or []

    report_text = "\n".join(
        [
            "INSIGHTS REPORT",
            f"SUMMARY: {summary}",
            "KEY INSIGHTS",
            *(f"- {x}" for x in insights_list[:50]),
            "DATA ISSUES",
            *(f"- {x}" for x in issues_list[:20]),
        ]
    ).strip()

    memory = (r.get("chat", []) or [])[-20:]  # keep last N turns
    history_text = format_memory(memory)

    llm = init_llm()
    prompt = PromptTemplate(
        input_variables=["report_text", "chat_history", "user_question"],
        template=chat_prompt,
    )
    chain = prompt | llm

    response = chain.invoke(
        {
            "report_text": report_text,
            "chat_history": history_text,
            "user_question": message,
        }
    )

    user_msg = {"id": uuid.uuid4().hex, "role": "user", "content": message, "ts": int(time.time() * 1000)}
    bot_msg = {
        "id": uuid.uuid4().hex,
        "role": "assistant",
        "content": (response.content or "").strip(),
        "ts": int(time.time() * 1000),
    }

    report_model.append_chat(report_id, user_msg)
    report_model.append_chat(report_id, bot_msg)

    return {"messages": [user_msg, bot_msg]}

