"""
MongoDB connection, single shared client for the whole app.

Uses PyMongo (sync) rather than Motor (async) for now - simpler to reason
about and fast enough at this scale. FastAPI runs sync route functions in
a thread pool automatically, so this doesn't block the event loop.
"""
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "deficiency_detector")

_client = None


def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _client[DB_NAME].users.create_index("username", unique=True)
        _client[DB_NAME].users.create_index("email", unique=True)
    return _client[DB_NAME]


def check_connection() -> bool:
    try:
        get_db().client.admin.command("ping")
        return True
    except ConnectionFailure:
        return False


def log_prediction(input_symptoms: list[str], predictions: list[dict], user_id=None) -> str:
    """Insert one prediction record. user_id stays None until Step 6 adds auth."""
    doc = {
        "user_id": user_id,
        "input_symptoms": input_symptoms,
        "predictions": predictions,
        "timestamp": datetime.now(timezone.utc),
    }
    result = get_db().predictions.insert_one(doc)
    return str(result.inserted_id)


def get_recent_predictions(limit: int = 10, user_id=None) -> list[dict]:
    query = {} if user_id is None else {"user_id": user_id}
    cursor = (get_db().predictions.find(query)
              .sort("timestamp", -1)
              .limit(limit))
    docs = []
    for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)
    return docs


def create_user(username: str, email: str, password_hash: str) -> str:
    doc = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.now(timezone.utc),
    }
    result = get_db().users.insert_one(doc)
    return str(result.inserted_id)


def get_user_by_username(username: str) -> dict | None:
    return get_db().users.find_one({"username": username})


def get_user_by_email(email: str) -> dict | None:
    return get_db().users.find_one({"email": email})


if __name__ == "__main__":
    if check_connection():
        print(f"Connected to MongoDB at {MONGO_URI}, database '{DB_NAME}'")
        count = get_db().predictions.count_documents({})
        print(f"Existing predictions in collection: {count}")
    else:
        print(f"FAILED to connect to MongoDB at {MONGO_URI}")
        print("Check that MongoDB is running: sc query MongoDB")
