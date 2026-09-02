#!/usr/bin/env python3
"""Static file server with gzip compression and production-like cache
headers, used by the CI Lighthouse step so the audit measures the site
the way a real CDN (GitHub Pages) serves it — compressed and cacheable.

Usage:
    python tools/lh_server.py [DIRECTORY] [PORT]
"""

import gzip
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "site").resolve()
PORT = int(sys.argv[2] if len(sys.argv) > 2 else "8765")

COMPRESSIBLE = {".html", ".css", ".js", ".json", ".svg", ".xml", ".webmanifest", ".txt", ".md"}
IMMUTABLE_PREFIXES = ("/assets/", "/pagefind/", "/downloads/", "/data/")

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("font/woff2", ".woff2")

_gz_cache = {}


class Handler(BaseHTTPRequestHandler):
    server_version = "LHStatic/1.0"

    def _resolve(self):
        path = self.path.split("?")[0].split("#")[0]
        if path.endswith("/"):
            path += "index.html"
        file_path = (ROOT / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(ROOT)):
            return None
        if file_path.is_dir():
            file_path /= "index.html"
        return file_path if file_path.exists() else None

    def do_GET(self):  # noqa: N802
        file_path = self._resolve()
        if file_path is None:
            self.send_error(404)
            return

        data = file_path.read_bytes()
        suffix = file_path.suffix.lower()
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

        use_gzip = (
            suffix in COMPRESSIBLE
            and "gzip" in self.headers.get("Accept-Encoding", "")
        )
        if use_gzip:
            if file_path not in _gz_cache:
                _gz_cache[file_path] = gzip.compress(data, 6)
            data = _gz_cache[file_path]

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        rel = "/" + str(file_path.relative_to(ROOT)).replace("\\", "/")
        if rel.startswith(IMMUTABLE_PREFIXES):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self):  # noqa: N802
        self.do_GET()

    def log_message(self, *args):  # keep CI logs quiet
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"serving {ROOT} on http://127.0.0.1:{PORT} (gzip + cache headers)")
    server.serve_forever()
