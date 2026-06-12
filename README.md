# Python HTTP Client and Server

An educational networking project that demonstrates how TCP, HTTP/1.1, TLS,
and HTML link parsing work using only the Python standard library.

The repository includes a small static web server and an interactive
command-line HTTP client. The client displays response status information and
headers, extracts links from HTML pages, and allows users to navigate between
them.

## Features

- HTTP and HTTPS connections over TCP sockets
- TLS certificate verification using Python's default SSL context
- Complete response reading without fixed-size body assumptions
- Support for `Transfer-Encoding: chunked`
- HTTP status line, header, and response body parsing
- Extraction of link text and targets from HTML
- Navigation through relative and absolute links
- Concurrent local static HTTP server
- Protection against directory traversal attacks
- Unit and integration tests
- No third-party dependencies

## Project Structure

```text
.
|-- Maximilian.py          # Interactive command-line HTTP client
|-- connection_helper.py   # Reusable TCP and TLS connection helper
|-- webserver.py           # Local static HTTP server
|-- example.html           # Example page containing navigation links
|-- link1.html
|-- link2.html
|-- tests/
|   `-- test_networking.py
|-- LICENSE
`-- README.md
```

## Requirements

- Python 3.10 or newer
- An available local TCP port, `8080` by default

The project uses only modules from the Python standard library. No package
installation is required.

## Getting Started

Clone the repository and enter its directory:

```bash
git clone https://github.com/Maxi3010/python-http-client-server.git
cd python-http-client-server
```

Start the local web server:

```bash
python webserver.py
```

The example website is now available at
[`http://127.0.0.1:8080/`](http://127.0.0.1:8080/).

Open a second terminal and start the command-line client:

```bash
python Maximilian.py
```

Enter the following URL to test the client against the local server:

```text
http://127.0.0.1:8080/example
```

The client displays the HTTP status, response headers, and a numbered list of
links. Enter a link number to follow it or `0` to exit.

## Server Configuration

The bind address, port, and document directory can be configured through
command-line options:

```bash
python webserver.py --host 127.0.0.1 --port 9000 --directory .
```

Display all available options:

```bash
python webserver.py --help
```

## Running the Tests

Run the complete test suite with:

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- HTTP status, header, and body parsing
- Chunked transfer decoding
- HTML link text and target extraction
- Client and server integration
- Missing-file responses
- Directory traversal protection

## Technical Notes

The client intentionally creates raw HTTP/1.1 requests to make the underlying
network exchange visible and understandable. It is designed as a learning
project and is not intended to replace production HTTP libraries such as
`urllib3` or `requests`.

The included server is intended for local development and demonstration. A
production deployment should use an established application or web server
with appropriate operational security controls.

## License

The source code derived from the provided starter project is distributed under
the BSD 3-Clause License. See [LICENSE](LICENSE) for details.
