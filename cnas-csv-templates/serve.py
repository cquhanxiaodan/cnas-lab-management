import http.server
import socketserver

PORT = 8080


class UTF8Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        super().do_GET()

    def end_headers(self):
        path = self.path.lower().split("?")[0].split("#")[0]
        if path.endswith((".html", ".htm", ".css", ".js", ".csv", ".md", ".txt", ".json")):
            self.send_header("Content-Type", self.headers.get("Content-Type", "text/plain") + "; charset=utf-8")
        super().end_headers()

    def guess_type(self, path):
        ctype = super().guess_type(path)
        lower = path.lower()
        if lower.endswith(".html") or lower.endswith(".htm"):
            return "text/html; charset=utf-8"
        if lower.endswith(".css"):
            return "text/css; charset=utf-8"
        if lower.endswith(".js"):
            return "application/javascript; charset=utf-8"
        if lower.endswith(".csv"):
            return "text/csv; charset=utf-8"
        if lower.endswith(".md"):
            return "text/markdown; charset=utf-8"
        if lower.endswith(".json"):
            return "application/json; charset=utf-8"
        return ctype


with socketserver.TCPServer(("", PORT), UTF8Handler) as httpd:
    print(f"Serving at port {PORT} with UTF-8")
    httpd.serve_forever()
