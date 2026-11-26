"""Run the same HTTP assertions using real HTTP messages in memory when loopback is blocked."""
import io
import sys
import unittest
from pathlib import Path
from http.client import HTTPResponse
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from test_http import HttpContract


class MemorySocket:
    def __init__(self, wire):
        self.input = io.BytesIO(wire)
        self.output = io.BytesIO()

    def makefile(self, *args, **kwargs):
        return self.input

    def sendall(self, data):
        self.output.write(data)


def exchange(self, method, path, url=None):
    data = b"" if url is None else urlencode([("url", url)]).encode()
    head = f"{method} {path} HTTP/1.0\r\nHost: localhost\r\nContent-Length: {len(data)}\r\n\r\n".encode()
    sock = MemorySocket(head + data)
    self.server.RequestHandlerClass(sock, ("127.0.0.1", 1), self.server)
    response = HTTPResponse(MemorySocket(sock.output.getvalue()))
    response.begin()
    return response.status, response.getheader("Location"), response.read().decode()


if __name__ == "__main__":
    HttpContract.request = exchange
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    sys.exit(not result.wasSuccessful())
