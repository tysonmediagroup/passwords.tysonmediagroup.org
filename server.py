#!/usr/bin/env python3
import http.server
import json
import os
import urllib.parse
import urllib.request

PORT = 8100
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
API_PROXY_BASE = "https://my.tysonmediagroup.org"

class PasswordsHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            try:
                req = urllib.request.Request(API_PROXY_BASE + self.path, method="HEAD")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        self.send_header(k, v)
                    self.end_headers()
                    return
            except Exception:
                pass
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            try:
                req = urllib.request.Request(API_PROXY_BASE + self.path, method="GET")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    body = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            except Exception:
                self.send_response(502)
                self.end_headers()
                return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length > 0 else b""
            try:
                req = urllib.request.Request(API_PROXY_BASE + self.path, data=raw, method="POST")
                req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))
                with urllib.request.urlopen(req, timeout=4) as resp:
                    body = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
                return
        super().do_POST()

if __name__ == "__main__":
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, PasswordsHandler)
    print(f"passwords.tysonmediagroup.org development server active on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
