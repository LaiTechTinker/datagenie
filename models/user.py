from bson import ObjectId
from extensions import get_db


def create(email: str, password_hash: str) -> dict:
    doc = {"email": email.lower(), "password_hash": password_hash}
    res = get_db().users.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def find_by_email(email: str) -> dict | None:
    return get_db().users.find_one({"email": email.lower()})


def find_by_id(user_id: str) -> dict | None:
    return get_db().users.find_one({"_id": ObjectId(user_id)})


def serialize(user: dict) -> dict:
    return {"id": str(user["_id"]), "email": user["email"]}
