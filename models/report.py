import time
from bson import ObjectId
from extensions import get_db


def create(dataset_id: str, file_path: str, insights: list, file_id: str, summary: str | None = None, issues: list | None = None) -> dict:
    doc = {
        "dataset_id": dataset_id,
        "file_path": file_path,
        "insights": insights,
        "file_id": file_id,
        "summary": summary or "",
        "issues": issues or [],
        "chat": [],
        "created_at": int(time.time() * 1000),
    }
    res = get_db().reports.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def get(report_id: str) -> dict | None:
    return get_db().reports.find_one({"_id": ObjectId(report_id)})


def append_chat(report_id: str, message: dict) -> None:
    get_db().reports.update_one({"_id": ObjectId(report_id)}, {"$push": {"chat": message}})


def serialize(r: dict) -> dict:
    return {
        "id": str(r["_id"]),
        "datasetId": r["dataset_id"],
        "file_path": r["file_path"],
        "file_id": r["file_id"],
        "summary": r.get("summary", ""),
        "insights": r.get("insights", []),
        "issues": r.get("issues", []),
        "chat": r.get("chat", []),
        "createdAt": r.get("created_at"),
    }
def update_file_path(report_id: str, file_path: str) -> None:
    get_db().reports.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"file_path": file_path}}
    )