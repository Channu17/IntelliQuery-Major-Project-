"""
Query history persistence layer.

Each query exchange (user question + AI response) is stored as a document
in the ``query_history`` MongoDB collection.  Documents belonging to the same
chat session share a ``session_id``.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from utils.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "query_history"


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def create_session_id() -> str:
    """Return a new unique session identifier."""
    return uuid.uuid4().hex


def save_history_entry(
    user_id: str,
    session_id: str,
    datasource_id: str,
    datasource_type: str,
    natural_query: str,
    generated_query: str,
    success: bool,
    row_count: Optional[int] = None,
    llm_used: Optional[str] = None,
    error: Optional[str] = None,
) -> str:
    """Persist a single query exchange and return its ``_id`` as string."""
    doc = {
        "user_id": user_id,
        "session_id": session_id,
        "datasource_id": datasource_id,
        "datasource_type": datasource_type,
        "natural_query": natural_query,
        "generated_query": generated_query,
        "success": success,
        "row_count": row_count,
        "llm_used": llm_used,
        "error": error,
        "created_at": datetime.now(timezone.utc),
    }
    result = get_db()[COLLECTION].insert_one(doc)
    return str(result.inserted_id)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_sessions(user_id: str, datasource_id: Optional[str] = None) -> List[dict]:
    """
    Return a list of sessions for a user, most-recent first.

    Each item contains:
      - session_id
      - datasource_id / datasource_type
      - title  (first query of the session)
      - message_count
      - last_queried_at
    """
    col = get_db()[COLLECTION]

    match_stage = {"user_id": user_id}
    if datasource_id:
        match_stage["datasource_id"] = datasource_id

    pipeline = [
        {"$match": match_stage},
        {"$sort": {"created_at": 1}},
        {
            "$group": {
                "_id": "$session_id",
                "datasource_id": {"$first": "$datasource_id"},
                "datasource_type": {"$first": "$datasource_type"},
                "title": {"$first": "$natural_query"},
                "message_count": {"$sum": 1},
                "last_queried_at": {"$max": "$created_at"},
            }
        },
        {"$sort": {"last_queried_at": -1}},
    ]

    sessions = []
    for doc in col.aggregate(pipeline):
        sessions.append({
            "session_id": doc["_id"],
            "datasource_id": doc["datasource_id"],
            "datasource_type": doc["datasource_type"],
            "title": doc["title"],
            "message_count": doc["message_count"],
            "last_queried_at": doc["last_queried_at"].isoformat() if doc.get("last_queried_at") else None,
        })

    return sessions


def get_session_messages(user_id: str, session_id: str) -> List[dict]:
    """Return all query entries for a session, oldest first."""
    col = get_db()[COLLECTION]
    cursor = col.find(
        {"user_id": user_id, "session_id": session_id},
        {"_id": 0},
    ).sort("created_at", 1)

    messages = []
    for doc in cursor:
        doc["created_at"] = doc["created_at"].isoformat() if doc.get("created_at") else None
        messages.append(doc)
    return messages


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_session(user_id: str, session_id: str) -> int:
    """Delete all entries for a session. Returns deleted count."""
    col = get_db()[COLLECTION]
    result = col.delete_many({"user_id": user_id, "session_id": session_id})
    return result.deleted_count
