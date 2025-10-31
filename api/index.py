import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from pymongo import MongoClient
from pymongo.errors import PyMongoError


_mongo_client = None


def _get_scores_collection():
    global _mongo_client
    mongodb_uri = os.environ.get("MONGODB_URI")
    if not mongodb_uri:
        raise RuntimeError("MONGODB_URI environment variable is not set")

    if _mongo_client is None:
        _mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

    return _mongo_client["leaderboard"]["scores"]


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path != "/api/leaderboard/top10":
            self.send_error(404, "Not Found")
            return

        try:
            collection = _get_scores_collection()
            top_scores = list(
                collection.find({}, {"_id": 0, "name": 1, "score": 1})
                .sort("score", -1)
                .limit(10)
            )
        except RuntimeError as exc:
            self._send_json_response(500, {"error": str(exc)})
            return
        except PyMongoError as exc:
            self._send_json_response(500, {"error": "Database error", "details": str(exc)})
            return

        self._send_json_response(200, top_scores)

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path != "/api/leaderboard/submit":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b""

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json_response(400, {"error": "Invalid JSON payload"})
            return

        name = payload.get("name")
        score = payload.get("score")

        if not isinstance(name, str) or not name.strip():
            self._send_json_response(400, {"error": "Field 'name' must be a non-empty string"})
            return

        if not isinstance(score, (int, float)):
            self._send_json_response(400, {"error": "Field 'score' must be a number"})
            return

        try:
            collection = _get_scores_collection()
            collection.insert_one({"name": name.strip(), "score": float(score)})
        except RuntimeError as exc:
            self._send_json_response(500, {"error": str(exc)})
            return
        except PyMongoError as exc:
            self._send_json_response(500, {"error": "Database error", "details": str(exc)})
            return

        self._send_json_response(201, {"status": "ok"})

    def _send_json_response(self, status_code, payload):
        response_bytes = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)
