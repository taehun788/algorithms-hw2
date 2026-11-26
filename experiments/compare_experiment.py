from src.hash_table import HashTable
from src.probing_table import ProbingTable
from .probe_experiment import chain_theory, measure, write_results


def probing_theory(alpha):
    inverse_free = 1 / (1 - alpha)
    return (1 + inverse_free) / 2, (1 + inverse_free**2) / 2


if __name__ == "__main__":
    methods = [("Chaining", HashTable, chain_theory),
               ("Linear probing", ProbingTable, probing_theory)]
    rows = measure([step / 10 for step in range(1, 10)], methods)
    write_results("comparison", rows)
    for row in rows:
        print(f"{row[0]:.1f} {row[2]:14} hit={row[3]:.3f} miss={row[4]:.3f}")
