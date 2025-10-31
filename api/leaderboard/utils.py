"""Shared helpers for leaderboard MongoDB access."""

import os
from typing import Any, Dict, List

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError


_mongo_client: MongoClient | None = None


class LeaderboardError(Exception):
    """Custom error for leaderboard operations."""


def _get_scores_collection() -> Collection:
    global _mongo_client
    mongodb_uri = os.environ.get("MONGODB_URI")
    if not mongodb_uri:
        raise LeaderboardError("MONGODB_URI environment variable is not set")

    if _mongo_client is None:
        _mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

    return _mongo_client["leaderboard"]["scores"]


def fetch_top_scores(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        collection = _get_scores_collection()
        return list(
            collection.find({}, {"_id": 0, "name": 1, "score": 1})
            .sort("score", -1)
            .limit(limit)
        )
    except PyMongoError as exc:
        raise LeaderboardError(f"Database error: {exc}") from exc


def submit_score(name: str, score: float) -> None:
    try:
        collection = _get_scores_collection()
        collection.insert_one({"name": name.strip(), "score": float(score)})
    except PyMongoError as exc:
        raise LeaderboardError(f"Database error: {exc}") from exc

