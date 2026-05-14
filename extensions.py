"""Shared singletons. Imported by app.py and services to avoid circular imports."""
from flask_socketio import SocketIO
from pymongo import MongoClient

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

# Mongo handle is set by app.py during init_extensions().
mongo_client: MongoClient | None = None
db = None


def init_mongo(uri: str, db_name: str):
    global mongo_client, db
    mongo_client = MongoClient(uri)
    db = mongo_client[db_name]
    # Indexes
    db.users.create_index("email", unique=True)
    db.datasets.create_index([("user_id", 1), ("created_at", -1)])
    db.reports.create_index("dataset_id")
    db.jobs.create_index([("user_id", 1), ("created_at", -1)])
    return db


def get_db():
    if db is None:
        raise RuntimeError("Mongo not initialized. Call init_mongo() first.")
    return db
