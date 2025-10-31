import json
from http.server import BaseHTTPRequestHandler

from .utils import LeaderboardError, fetch_top_scores


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            top_scores = fetch_top_scores(limit=10)
        except LeaderboardError as exc:
            self._send_json_response(500, {"error": str(exc)})
            return

        self._send_json_response(200, top_scores)

    def do_POST(self):
        self.send_error(405, "Method Not Allowed")

    def _send_json_response(self, status_code, payload):
        response_bytes = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

