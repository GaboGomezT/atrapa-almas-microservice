import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """HTTP handler that exposes the leaderboard API entry point."""

    ALLOWED_METHODS = "GET, OPTIONS"

    def do_GET(self):
        message = {
            "message": "Leaderboard API entry point",
            "endpoints": {
                "GET /api/leaderboard/top10": "Fetch top 10 leaderboard scores",
                "POST /api/leaderboard/submit": "Submit a score with {name, score}",
            },
        }
        self._send_json_response(200, message)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        self.send_error(405, "Method Not Allowed")

    def _send_json_response(self, status_code, payload):
        response_bytes = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", self.ALLOWED_METHODS)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()
