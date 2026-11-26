"""Export actual runtime table state for the course's two-URL collision example."""
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.hash_table import HashTable, horner
from src.probing_table import ProbingTable
from src.shortener import Shortener
from src.server import CSS


def render():
    urls = ("https://github.com", "https://docs.python.org/3/")
    sections = []
    for factory, name in [(HashTable, "개별 체이닝"), (ProbingTable, "선형 탐지")]:
        app = Shortener(factory)
        rows = []
        for url in urls:
            code = app.shorten(url)
            start = horner(url, app.urls.capacity)
            index = next(i for i, key, _ in app.urls.entries() if key == url)
            if factory is ProbingTable:
                path = " → ".join(str((start + step) % app.urls.capacity) for step in range((index-start) % app.urls.capacity+1))
                outcome = "탐지 경로 " + path
            else:
                chain = [value for i, _, value in app.urls.entries() if i == index]
                outcome = "코드 " + " → ".join(chain + ["NULL"])
            rows.append(f"<tr><td>{escape(url)}</td><td>{code}</td><td>{start}</td><td>{index}</td><td>{outcome}</td></tr>")
        trace = []
        horner(urls[1], app.urls.capacity, trace)
        steps = "".join(f"<li>(31 × {old} + {ord(c)}) mod 16 = {new} [{escape(c)}]</li>" for c, old, new in trace)
        sections.append(f"<h2>{name}</h2><table><tr><th>입력한 순서</th><th>코드</th><th>처음 칸</th><th>저장 칸</th><th>삽입 직후</th></tr>"
                        + "".join(rows) + f"</table><details><summary>두 번째 주소의 호너 해시 계산</summary><ol>{steps}</ol></details>")
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>충돌 확인 · URL 단축기</title><style>{CSS}</style></head><body><h1>같은 5번 칸에서 일어난 충돌</h1>'
            '<p>빈 16칸 테이블에서 주소 두 개를 차례로 넣은 실제 실행 결과.</p>' + "".join(sections) + "</body></html>")


if __name__ == "__main__":
    (ROOT / "experiments" / "collision.html").write_text(render(), encoding="utf-8")
