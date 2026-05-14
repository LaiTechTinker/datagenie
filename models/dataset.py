import time
from bson import ObjectId
from extensions import get_db


def create(user_id: str, name: str, rows: list, columns: list, file_path: str) -> dict:
    doc = {
        "user_id": user_id,
        "name": name,
        "rows": rows,
        "columns": columns,
        "file_path": file_path,
        "row_count": len(rows),
        "created_at": int(time.time() * 1000),
    }
    res = get_db().datasets.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def list_for_user(user_id: str) -> list:
    cur = get_db().datasets.find(
        {"user_id": user_id},
        {"rows": 0},  # exclude rows from list
    ).sort("created_at", -1)
    return list(cur)


def get(user_id: str, dataset_id: str) -> dict | None:
    return get_db().datasets.find_one({"_id": ObjectId(dataset_id), "user_id": user_id})


def delete(user_id: str, dataset_id: str) -> int:
    res = get_db().datasets.delete_one({"_id": ObjectId(dataset_id), "user_id": user_id})
    return res.deleted_count


def serialize(d: dict, include_rows: bool = False, max_rows: int = 100) -> dict:
    out = {
        "id": str(d["_id"]),
        "name": d["name"],
        "columns": d.get("columns", []),
        "rowCount": d.get("row_count", len(d.get("rows", []))),
        "createdAt": d.get("created_at"),
    }
    if include_rows:
        out["rows"] = d.get("rows", [])[:max_rows]
    return out
