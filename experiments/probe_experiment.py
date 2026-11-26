"""Reproducible measurements and a two-panel SVG. Run from the repository root."""
import csv
import math
import random
from pathlib import Path
from statistics import mean

from src.hash_table import HashTable

OUT = Path(__file__).resolve().parent
CAPACITY = 4093
REPEATS = 6
MISSES = 2000
SEED = 20261120
HEADER = ("target_load", "actual_load", "method", "hit", "miss", "hit_theory", "miss_theory")


def keys_for(count, seed):
    rng = random.Random(seed)
    return [f"https://example.org/{n:013x}" for n in rng.sample(range(2**51), count)]


def measure(loads, methods):
    rows = []
    for target in loads:
        size = round(CAPACITY * target)
        alpha = size / CAPACITY
        totals = [[[], []] for _ in methods]
        for trial in range(REPEATS):
            keys = keys_for(size + MISSES, SEED + trial)
            present, absent = keys[:size], keys[size:]
            for index, (_, factory, _) in enumerate(methods):
                table = factory(CAPACITY, max_load=None)
                for key in present:
                    table.put(key, "v")
                totals[index][0].append(mean(table.find(key)[1] for key in present))
                totals[index][1].append(mean(table.find(key)[1] for key in absent))
        for (label, _, theory), (hits, misses) in zip(methods, totals):
            rows.append((target, alpha, label, mean(hits), mean(misses), *theory(alpha)))
    return rows


def write_results(stem, rows):
    with (OUT / (stem + ".csv")).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
        writer.writerows(rows)
    (OUT / (stem + ".svg")).write_text(chart(rows), encoding="utf-8")


def chart(rows):
    colors = {"Chaining": "#176754", "Linear probing": "#a63f22"}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 460" role="img" aria-label="Mean successful and unsuccessful search costs by load">',
             '<rect width="1000" height="460" fill="white"/>',
             '<g font-family="Arial, sans-serif" fill="#202824">',
             '<text x="50" y="39" font-size="24" font-weight="bold">Search cost versus load factor</text>',
             '<text x="50" y="67" font-size="15">Chaining: compared nodes  |  Linear probing: inspected slots  |  Solid: measured  |  Dashed: theoretical</text>']
    min_x = min(r[0] for r in rows)
    max_x = max(r[0] for r in rows)
    for panel, title in enumerate(("Successful lookup", "Unsuccessful lookup")):
        left, top, width, height = 67 + 492 * panel, 120, 392, 235
        high = math.ceil(max(max(row[3 + panel], row[5 + panel]) for row in rows) / 2) * 2
        parts.append(f'<text x="{left}" y="{top-15}" font-size="18">{title}</text>')
        for tick in range(5):
            y = top + height * (1 - tick / 4)
            parts.append(f'<path d="M{left},{y}h{width}" stroke="#d8dfdd"/><text x="{left-8}" y="{y+4}" text-anchor="end" font-size="12">{high*tick/4:g}</text>')
        for xval in sorted({r[0] for r in rows}):
            x = left + width * (xval - min_x) / (max_x - min_x)
            parts.append(f'<text x="{x:.1f}" y="379" text-anchor="middle" font-size="12">{xval:g}</text>')
        parts.append(f'<text x="{left+width/2}" y="403" text-anchor="middle" font-size="14">Load factor (N/M)</text>')
        for label in dict.fromkeys(r[2] for r in rows):
            series = [row for row in rows if row[2] == label]
            color = colors[label]
            for column, dash in ((3 + panel, ""), (5 + panel, 'stroke-dasharray="6 4"')):
                coords = [(left + width * (r[0] - min_x) / (max_x - min_x),
                           top + height * (1 - r[column] / high)) for r in series]
                points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)
                parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.2" {dash}/>')
                if not dash:
                    for x, y in coords:
                        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{color}"/>')
    for i, label in enumerate(dict.fromkeys(r[2] for r in rows)):
        x = 50 + i * 190
        parts.append(f'<rect x="{x}" y="428" width="16" height="6" fill="{colors[label]}"/><text x="{x+23}" y="437" font-size="15">{label}</text>')
    return "".join(parts) + "</g></svg>"


def chain_theory(alpha):
    return 1 + alpha / 2, alpha


if __name__ == "__main__":
    rows = measure([0.25, 0.5, 1, 2, 4], [("Chaining", HashTable, chain_theory)])
    write_results("results", rows)
    for row in rows:
        print(f"load={row[0]:g} hit={row[3]:.3f} miss={row[4]:.3f}")
