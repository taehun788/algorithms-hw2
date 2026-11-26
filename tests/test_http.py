import threading
import unittest
from http.client import HTTPConnection
from urllib.parse import urlencode

from src.hash_table import HashTable
from src.server import build_server


class HttpContract:
    factory = None
    probing = False

    def setUp(self):
        self.server = build_server(("127.0.0.1", 0), self.factory, self.probing)
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.02), daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def request(self, method, path, url=None):
        client = HTTPConnection(*self.server.server_address)
        try:
            client.request(method, path, None if url is None else urlencode([("url", url)]))
            response = client.getresponse()
            return response.status, response.getheader("Location"), response.read().decode()
        finally:
            client.close()

    def test_full_flow(self):
        self.assertIn("긴 URL", self.request("GET", "/")[2])
        a, b = "https://github.com", "https://docs.python.org/3/"
        for code, url in [("1", a), ("2", b), ("1", a)]:
            status, _, body = self.request("POST", "/shorten", url)
            self.assertEqual(status, 200)
            self.assertIn(f'href="/{code}"', body)
            self.assertEqual(self.request("GET", "/" + code)[:2], (302, url))
        html = self.request("GET", "/table")[2]
        self.assertIn("호너 계산", html)
        self.assertIn("5 → 6" if self.probing else "NULL", html)
        self.assertEqual(self.request("POST", "/shorten", a + " ")[0], 400)
        self.assertEqual(self.request("GET", "/missing")[0], 404)


class ChainingHttpTests(HttpContract, unittest.TestCase):
    factory = HashTable
