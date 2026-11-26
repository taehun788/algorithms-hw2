from urllib.parse import urlsplit

from .base62 import encode
from .hash_table import HashTable


def validate_url(url):
    if not isinstance(url, str) or not 1 <= len(url) <= 2048:
        raise ValueError("URL은 1~2048자여야 합니다.")
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError("URL에 공백이나 제어 문자를 포함할 수 없습니다.")
    try:
        parts = urlsplit(url)
        port = parts.port
        hostname = parts.hostname
    except ValueError as exc:
        raise ValueError("주소 또는 포트 형식이 잘못되었습니다.") from exc
    if parts.scheme not in ("http", "https") or not hostname:
        raise ValueError("호스트가 있는 http 또는 https URL을 입력하세요.")


class Shortener:
    def __init__(self, factory=HashTable, capacity=16):
        self.urls = factory(capacity)
        self.codes = factory(capacity)

    def shorten(self, url):
        validate_url(url)
        existing = self.urls.get(url)
        if existing is not None:
            return existing
        code = encode(len(self.urls) + 1)
        self.urls.put(url, code)
        self.codes.put(code, url)
        return code

    def resolve(self, code):
        return self.codes.get(code)
