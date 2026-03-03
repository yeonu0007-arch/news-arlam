import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from app import handler


class ScraperHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        result = handler(body, None)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def log_message(self, format, *args):
        pass  # 기본 로그 억제


if __name__ == "__main__":
    port = 9000
    server = HTTPServer(("localhost", port), ScraperHandler)
    print(f"Scraper local server running on http://localhost:{port}")
    server.serve_forever()
