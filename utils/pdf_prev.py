import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from utils.S3 import upload_pdf_to_s3


def generate_pdf_report(report_text: str, report_id: str) -> str:
    """
    Converts AI-generated report text into a styled PDF,
    uploads it to S3, deletes the temp file and returns the S3 key.
    """
    BASE_DIR = os.getcwd()
    output_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(output_dir, exist_ok=True)

    file_name = f"report_{report_id}.pdf"
    temp_path = os.path.join(output_dir, file_name)

    # Build PDF locally
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    lines = report_text.split("\n")
    for line in lines:
        line = line.strip()

        if not line:
            elements.append(Spacer(1, 10))
            continue

        if line.isupper():
            elements.append(Paragraph(f"<b>{line}</b>", styles["Heading2"]))

        elif line.startswith("-"):
            elements.append(Paragraph(line, styles["Normal"]))

        elif "|" in line:
            table_data = parse_table(report_text)
            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 10))
                break

        else:
            elements.append(Paragraph(line, styles["Normal"]))

        elements.append(Spacer(1, 8))

    doc.build(elements)

    # Upload to S3 then clean up temp file
    s3_key = f"reports/{report_id}/{file_name}"
    try:
        upload_pdf_to_s3(temp_path, s3_key)
    except RuntimeError:
        raise
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return s3_key


def parse_table(text: str):
    """
    Extracts simple tables from LLM output (pipe-separated)
    """
    lines = text.split("\n")
    table_lines = []

    for line in lines:
        if "|" in line:
            row = [cell.strip() for cell in line.split("|") if cell.strip()]
            if row:
                table_lines.append(row)

    return table_lines if len(table_lines) > 1 else None