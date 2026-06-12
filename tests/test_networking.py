from __future__ import annotations

from pathlib import Path
import threading
import unittest

from Maximilian import HttpResponse, decode_chunked_body, extract_links, fetch
from webserver import StaticHTTPServer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class HttpParsingTests(unittest.TestCase):
    def test_parses_status_headers_and_body(self) -> None:
        response = HttpResponse.from_bytes(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"X-Test: value:with:colons\r\n\r\n"
            b"hello"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-test"], "value:with:colons")
        self.assertEqual(response.text(), "hello")

    def test_decodes_chunked_body(self) -> None:
        body = decode_chunked_body(b"4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n")
        self.assertEqual(body, b"Wikipedia")

    def test_extracts_link_text_and_target(self) -> None:
        links = extract_links('<a href="page.html">Example <strong>page</strong></a>')
        self.assertEqual(links[0].text, "Example page")
        self.assertEqual(links[0].target, "page.html")


class ServerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = StaticHTTPServer(("127.0.0.1", 0), PROJECT_ROOT)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_serves_example_page_and_links(self) -> None:
        response = fetch(f"{self.base_url}/example")
        links = extract_links(response.text())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [link.target for link in links],
            ["link1.html", "link2.html"],
        )

    def test_returns_404_for_missing_file(self) -> None:
        response = fetch(f"{self.base_url}/missing.html")
        self.assertEqual(response.status_code, 404)

    def test_blocks_path_traversal(self) -> None:
        response = fetch(f"{self.base_url}/../README.md")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
