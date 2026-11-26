import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, quote, urlsplit

from .hash_table import HashTable, horner
from .shortener import Shortener

CSS = """
*{box-sizing:border-box}body{max-width:1000px;margin:auto;padding:36px 22px;color:#192f2a;background:#fafbf8;font:16px/1.55 system-ui,sans-serif}
nav{display:flex;gap:22px;border-bottom:1px solid #bbc9c3;padding-bottom:14px}a{color:#176252}
h1{font-size:clamp(28px,5vw,44px);letter-spacing:-.04em;margin:28px 0 12px}
label{display:block;margin:20px 0 7px}input,button{padding:11px 14px;font:inherit;border-radius:5px}
input{width:min(100%,600px);border:1px solid #879d92}button{background:#175b4a;color:white;border:0;cursor:pointer}
table{width:100%;border-collapse:collapse;background:white}th,td{padding:9px 12px;border:1px solid #cdd7cd;text-align:left;vertical-align:top}
td{overflow-wrap:anywhere}summary{cursor:pointer}code{color:#354f44}details{margin:4px 0}ol{font-family:monospace}.result{padding:12px;background:#e3f0e6}
"""


def page(title, body):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>{CSS}</style></head><body><nav><a href="/">URL 단축기</a><a href="/table">해시 테이블</a></nav>'
            f'<main><h1>{title}</h1>{body}</main><script>for(const a of document.querySelectorAll("a.short")) a.textContent=a.href;</script></body></html>')


def short_link(code):
    return f'<a class="short" href="/{code}">/{code}</a>'


def entry_detail(table, index, url, code, probing):
    trace = []
    start = horner(url, table.capacity, trace)
    steps = "".join(f"<li>(31 × {old} + {ord(c)}) mod {table.capacity} = {new} [{escape(c)}]</li>"
                    for c, old, new in trace)
    path = str(start)
    if probing:
        count = (index - start) % table.capacity + 1
        path = " → ".join(str((start + step) % table.capacity) for step in range(count))
    return (f'<details><summary>{escape(url)} · 코드 {code}</summary>{short_link(code)}'
            f'<p>처음 칸 {start} · 방문 경로 {path} · 저장 칸 {index}</p>'
            f'<details><summary>문자별 호너 계산</summary><ol>{steps}</ol></details></details>')


def table_page(app, probing):
    table = app.urls
    cells = [[] for _ in range(table.capacity)]
    for index, key, value in table.entries():
        cells[index].append(entry_detail(table, index, key, value, probing))
    rows = []
    for index, items in enumerate(cells):
        content = "빈칸" if probing else " → ".join(items + ["NULL"])
        if probing and items:
            content = items[0]
        rows.append(f'<tr><th scope="row">{index}</th><td>{content}</td></tr>')
    name = "선형 탐지" if probing else "개별 체이닝"
    return page(name, f'<p>URL → 코드 · 원소 {len(table)}개 / {table.capacity}칸 · 적재율 {table.load_factor:.3f}</p>'
                '<table><thead><tr><th>칸</th><th>저장한 URL과 계산 과정</th></tr></thead><tbody>'
                + "".join(rows) + "</tbody></table>")


FORM = ('<form method="post" action="/shorten"><label for="url">긴 URL</label>'
        '<input id="url" name="url" type="text" inputmode="url" placeholder="https://example.com" required> '
        '<button>줄이기</button></form>')


def build_server(address, factory=HashTable, probing=False):
    app = Shortener(factory)

    class Handler(BaseHTTPRequestHandler):
        def show(self, status, body):
            payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                self.show(200, page("URL 단축기", FORM))
            elif path == "/table":
                self.show(200, table_page(app, probing))
            else:
                url = app.resolve(path[1:])
                if url is None:
                    self.show(404, page("링크를 찾을 수 없습니다", FORM))
                    return
                self.send_response(302)
                self.send_header("Location", quote(url, safe=":/?#[]@!$&'()*+,;=%-._~"))
                self.end_headers()

        def do_POST(self):
            if self.path != "/shorten":
                self.show(404, page("없는 경로", FORM))
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 32768:
                    raise ValueError("입력 크기를 확인하세요.")
                data = parse_qsl(self.rfile.read(length).decode("utf-8"), keep_blank_values=True, max_num_fields=2)
                if len(data) != 1 or data[0][0] != "url":
                    raise ValueError("URL 하나를 입력하세요.")
                code = app.shorten(data[0][1])
            except ValueError as exc:
                self.show(400, page("입력 오류", f'<p>{escape(str(exc))}</p>{FORM}'))
                return
            self.show(200, page("단축 링크", f'<p class="result">{short_link(code)}</p>{FORM}'))

    return HTTPServer(address, Handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", choices=("chain",), default="chain")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with build_server(("0.0.0.0", args.port)) as server:
        print(f"Serving at http://localhost:{args.port} ({args.table})", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
