#!/usr/bin/env python3
"""Interactive command-line browser implemented with raw HTTP sockets."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit

from connection_helper import HttpConnectionHelper


@dataclass(frozen=True)
class Link:
    """A link extracted from an HTML document."""

    text: str
    target: str


@dataclass(frozen=True)
class HttpResponse:
    """Parsed parts of a basic HTTP response."""

    status_line: str
    status_code: int
    headers: dict[str, str]
    body: bytes

    @classmethod
    def from_bytes(cls, payload: bytes) -> "HttpResponse":
        header_data, separator, body = payload.partition(b"\r\n\r\n")
        if not separator:
            raise ValueError("The server response does not contain HTTP headers.")

        lines = header_data.decode("iso-8859-1").split("\r\n")
        status_line = lines[0]
        status_parts = status_line.split(" ", maxsplit=2)
        if len(status_parts) < 2 or not status_parts[1].isdigit():
            raise ValueError(f"Invalid HTTP status line: {status_line}")

        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            name, value = line.split(":", maxsplit=1)
            headers[name.strip().lower()] = value.strip()

        if "chunked" in headers.get("transfer-encoding", "").lower():
            body = decode_chunked_body(body)

        return cls(status_line, int(status_parts[1]), headers, body)

    def text(self) -> str:
        """Decode the response body using the declared charset."""
        content_type = self.headers.get("content-type", "")
        charset_match = re.search(r"charset=([\w.-]+)", content_type, re.I)
        charset = charset_match.group(1) if charset_match else "utf-8"
        try:
            return self.body.decode(charset)
        except (LookupError, UnicodeDecodeError):
            return self.body.decode("utf-8", errors="replace")


def decode_chunked_body(payload: bytes) -> bytes:
    """Decode an HTTP/1.1 chunked response body."""
    position = 0
    decoded = bytearray()

    while True:
        line_end = payload.find(b"\r\n", position)
        if line_end == -1:
            raise ValueError("Invalid chunked response: missing chunk size.")

        size_text = payload[position:line_end].split(b";", maxsplit=1)[0]
        try:
            chunk_size = int(size_text, 16)
        except ValueError as error:
            raise ValueError("Invalid chunked response: malformed chunk size.") from error

        position = line_end + 2
        if chunk_size == 0:
            return bytes(decoded)

        chunk_end = position + chunk_size
        if chunk_end + 2 > len(payload) or payload[chunk_end:chunk_end + 2] != b"\r\n":
            raise ValueError("Invalid chunked response: incomplete chunk.")

        decoded.extend(payload[position:chunk_end])
        position = chunk_end + 2


class LinkParser(HTMLParser):
    """Collect links and their visible text."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[Link] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() != "a":
            return
        self._current_href = dict(attrs).get("href")
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        text = " ".join("".join(self._current_text).split())
        self.links.append(Link(text or self._current_href, self._current_href))
        self._current_href = None
        self._current_text = []


def normalize_url(value: str) -> str:
    """Add an HTTP scheme when the user entered only a host name."""
    value = value.strip()
    if not value:
        raise ValueError("Please enter a URL.")
    if "://" not in value:
        return f"http://{value}"
    return value


def fetch(url: str, timeout: float = 10.0) -> HttpResponse:
    """Fetch one HTTP(S) URL using the socket helper."""
    normalized_url = normalize_url(url)
    parsed = urlsplit(normalized_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http:// and https:// URLs are supported.")
    if not parsed.hostname:
        raise ValueError("The URL does not contain a valid host name.")

    secure = parsed.scheme == "https"
    port = parsed.port or (443 if secure else 80)
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"

    default_port = 443 if secure else 80
    host_header = parsed.hostname
    if port != default_port:
        host_header = f"{host_header}:{port}"

    request = (
        f"GET {target} HTTP/1.1\r\n"
        f"Host: {host_header}\r\n"
        "Accept: text/html, */*;q=0.8\r\n"
        "Connection: close\r\n"
        "User-Agent: Networking-Maximilian/1.0\r\n\r\n"
    )

    with HttpConnectionHelper(timeout=timeout) as connection:
        connection.connect(parsed.hostname, port, secure)
        connection.send_request(request)
        return HttpResponse.from_bytes(connection.receive_all())


def extract_links(html: str) -> list[Link]:
    """Return all links contained in an HTML document."""
    parser = LinkParser()
    parser.feed(html)
    return parser.links


def print_response(response: HttpResponse) -> None:
    """Display status and headers in a readable format."""
    print(f"\n{response.status_line}")
    for name, value in response.headers.items():
        print(f"{name}: {value}")


def run_browser(start_url: str) -> None:
    """Navigate through HTML links until the user chooses to exit."""
    current_url = normalize_url(start_url)

    while True:
        try:
            response = fetch(current_url)
        except (OSError, ValueError) as error:
            print(f"Request failed: {error}")
            return

        print_response(response)
        links = extract_links(response.text())
        if not links:
            print("\nNo links found on this page.")
            return

        print()
        for number, link in enumerate(links, start=1):
            print(f"[{number}] {link.text} -> {urljoin(current_url, link.target)}")

        choice = input("\nSelect a link or enter 0 to exit: ").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(links):
            print("Invalid selection. Please try again.")
            continue

        current_url = urljoin(current_url, links[int(choice) - 1].target)


def main() -> None:
    start_url = input("Enter the website you want to visit: ")
    run_browser(start_url)


if __name__ == "__main__":
    main()
