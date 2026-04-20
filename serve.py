"""Minimal static file server for local development.

Usage:
    python serve.py            # serves on http://localhost:8000
    python serve.py 8080       # custom port

The app loads JSON/audio via fetch(), which browsers block for file:// URLs.
Running this server avoids that restriction.
"""
from __future__ import annotations

import http.server
import socketserver
import sys
from pathlib import Path


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".mp3": "audio/mpeg",
        ".json": "application/json; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".html": "text/html; charset=utf-8",
    }

    def end_headers(self) -> None:  # noqa: D401
        # Prevent aggressive caching during development.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    root = Path(__file__).resolve().parent
    import os

    os.chdir(root)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving {root} at http://localhost:{port}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye.")


if __name__ == "__main__":
    main()
