#!/usr/bin/env python3
"""Minimal local HTTP server for the example pages."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlsplit


class StaticHTTPServer(ThreadingHTTPServer):
    """HTTP server with an explicit document root."""

    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        document_root: Path,
    ) -> None:
        super().__init__(server_address, CustomHttpRequestHandler)
        self.document_root = document_root.resolve()


class CustomHttpRequestHandler(BaseHTTPRequestHandler):
    """Serve files while keeping all requests inside the document root."""

    server: StaticHTTPServer

    def do_GET(self) -> None:
        request_path = unquote(urlsplit(self.path).path)
        relative_path = "example.html" if request_path in {"/", "/example"} else request_path.lstrip("/")
        file_path = (self.server.document_root / relative_path).resolve()

        try:
            file_path.relative_to(self.server.document_root)
        except ValueError:
            self.send_error(403, "Forbidden")
            return

        if not file_path.is_file():
            self.send_error(404, "Not found")
            return

        try:
            content = file_path.read_bytes()
        except OSError:
            self.send_error(500, "Unable to read file")
            return

        content_type, _ = mimetypes.guess_type(file_path.name)
        content_type = content_type or "application/octet-stream"
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="address to bind")
    parser.add_argument("--port", type=int, default=8080, help="TCP port")
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory containing the HTML files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = StaticHTTPServer((args.host, args.port), args.directory)
    print(f"Server running at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
