import json
from http.server import BaseHTTPRequestHandler

from .utils import LeaderboardError, submit_score


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
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
            submit_score(name.strip(), float(score))
        except LeaderboardError as exc:
            self._send_json_response(500, {"error": str(exc)})
            return

        self._send_json_response(201, {"status": "ok"})

    def do_GET(self):
        self.send_error(405, "Method Not Allowed")

    def _send_json_response(self, status_code, payload):
        response_bytes = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

