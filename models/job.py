import time
from bson import ObjectId
from extensions import get_db


def create(user_id: str, dataset_id: str, target: str, problem_type: str,
           test_size: float, random_state: int) -> dict:
    doc = {
        "user_id": user_id,
        "dataset_id": dataset_id,
        "target": target,
        "problem_type": problem_type,
        "test_size": test_size,
        "random_state": random_state,
        "status": "queued",
        "progress": 0,
        "logs": [],
        "results": None,
        "created_at": int(time.time() * 1000),
    }
    res = get_db().jobs.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def update(job_id: str, **fields) -> None:
    get_db().jobs.update_one({"_id": ObjectId(job_id)}, {"$set": fields})


def push_log(job_id: str, line: str) -> None:
    get_db().jobs.update_one({"_id": ObjectId(job_id)}, {"$push": {"logs": line}})


def get(job_id: str) -> dict | None:
    return get_db().jobs.find_one({"_id": ObjectId(job_id)})


def list_for_user(user_id: str) -> list:
    return list(get_db().jobs.find({"user_id": user_id}).sort("created_at", -1))


def serialize(j: dict) -> dict:
    return {
        "id": str(j["_id"]),
        "datasetId": j["dataset_id"],
        "target": j["target"],
        "problemType": j["problem_type"],
        "testSize": j["test_size"],
        "randomState": j["random_state"],
        "status": j["status"],
        "progress": j["progress"],
        "logs": j.get("logs", []),
        "results": j.get("results"),
        "createdAt": j.get("created_at"),
    }
