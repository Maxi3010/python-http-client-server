#!/usr/bin/env python3
"""Small TCP/TLS helper used by the command-line HTTP client."""

from __future__ import annotations

import socket
import ssl


class HttpConnectionHelper:
    """Manage one TCP connection and optionally wrap it in TLS."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.internal_connection: socket.socket | ssl.SSLSocket | None = None

    def connect(
        self,
        host: str,
        port: int | None = None,
        secure: bool = False,
    ) -> None:
        """Open a connection to *host* using HTTP or HTTPS defaults."""
        self.close()
        connection_port = port if port is not None else (443 if secure else 80)
        connection = socket.create_connection(
            (host, connection_port),
            timeout=self.timeout,
        )

        if secure:
            context = ssl.create_default_context()
            connection = context.wrap_socket(connection, server_hostname=host)

        self.internal_connection = connection

    def send_request(self, request: str | bytes) -> None:
        """Send the complete request."""
        if self.internal_connection is None:
            raise RuntimeError("No connection has been established.")

        payload = request.encode("utf-8") if isinstance(request, str) else request
        self.internal_connection.sendall(payload)

    def receive_response(self, chunk_size: int = 4096) -> bytes:
        """Receive one response chunk."""
        if self.internal_connection is None:
            raise RuntimeError("No connection has been established.")
        return self.internal_connection.recv(chunk_size)

    def receive_all(self, chunk_size: int = 4096) -> bytes:
        """Read until the remote peer closes the connection."""
        chunks: list[bytes] = []
        while True:
            chunk = self.receive_response(chunk_size)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    def close(self) -> None:
        """Close the active connection, if any."""
        if self.internal_connection is not None:
            self.internal_connection.close()
            self.internal_connection = None

    def __enter__(self) -> "HttpConnectionHelper":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


if __name__ == "__main__":
    with HttpConnectionHelper() as connection:
        connection.connect("localhost", 8080)
        connection.send_request(
            "GET /example HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Connection: close\r\n\r\n"
        )
        print(connection.receive_all().decode("utf-8", errors="replace"))
