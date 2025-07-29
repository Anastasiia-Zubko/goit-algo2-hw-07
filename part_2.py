from __future__ import annotations

import statistics
import sys
import timeit
from dataclasses import dataclass
from typing import List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

# Splay Tree

@dataclass
class _Node:
    key: int
    value: int
    left: "_Node | None" = None
    right: "_Node | None" = None
    parent: "_Node | None" = None


class SplayTree:

    def __init__(self) -> None:
        self.root: _Node | None = None

    def _right_rotate(self, x: _Node) -> None:
        y = x.left
        if y is None:
            return
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def _left_rotate(self, x: _Node) -> None:
        y = x.right
        if y is None:
            return
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _splay(self, x: _Node) -> None:
        while x.parent:
            if x.parent.parent is None:  # Zig
                if x.parent.left == x:
                    self._right_rotate(x.parent)
                else:
                    self._left_rotate(x.parent)
            elif x.parent.left == x and x.parent.parent.left == x.parent:  # Zig‑zig
                self._right_rotate(x.parent.parent)
                self._right_rotate(x.parent)
            elif x.parent.right == x and x.parent.parent.right == x.parent:  # Zig‑zig
                self._left_rotate(x.parent.parent)
                self._left_rotate(x.parent)
            elif x.parent.left == x and x.parent.parent.right == x.parent:  # Zig‑zag
                self._right_rotate(x.parent)
                self._left_rotate(x.parent)
            else:  # Zig‑zag
                self._left_rotate(x.parent)
                self._right_rotate(x.parent)

    def _find_node(self, key: int) -> _Node | None:
        node = self.root
        while node:
            if key == node.key:
                self._splay(node)
                return node
            elif key < node.key:
                if node.left:
                    node = node.left
                else:
                    self._splay(node)
                    return None
            else:
                if node.right:
                    node = node.right
                else:
                    self._splay(node)
                    return None
        return None

    def get(self, key: int) -> int | None:
        node = self._find_node(key)
        return node.value if node else None

    def insert(self, key: int, value: int) -> None:
        if self.root is None:
            self.root = _Node(key, value)
            return
        node = self.root
        while True:
            if key == node.key:
                node.value = value
                self._splay(node)
                return
            elif key < node.key:
                if node.left:
                    node = node.left
                else:
                    node.left = _Node(key, value, parent=node)
                    self._splay(node.left)
                    return
            else:
                if node.right:
                    node = node.right
                else:
                    node.right = _Node(key, value, parent=node)
                    self._splay(node.right)
                    return


from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


def fibonacci_splay(n: int, tree: SplayTree) -> int:
    cached = tree.get(n)
    if cached is not None:
        return cached

    if n < 2:
        tree.insert(n, n)
        return n

    val = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)
    tree.insert(n, val)
    return val


def measure_times(n_values: List[int], repeats: int = 5) -> Tuple[List[float], List[float]]:
    lru_results: List[float] = []
    splay_results: List[float] = []

    for n in n_values:
        # LRU Cache
        fibonacci_lru.cache_clear()
        stmt_lru = lambda nn=n: fibonacci_lru(nn)
        lru_time = statistics.mean(timeit.repeat(stmt_lru, repeat=repeats, number=1))
        lru_results.append(lru_time)

        # Splay Tree Cache
        def stmt_splay(nn=n):
            tree = SplayTree()
            return fibonacci_splay(nn, tree)

        splay_time = statistics.mean(timeit.repeat(stmt_splay, repeat=repeats, number=1))
        splay_results.append(splay_time)

    return lru_results, splay_results


def main() -> None:
    sys.setrecursionlimit(2_000)

    n_vals = list(range(0, 1000, 50))
    lru_times, splay_times = measure_times(n_vals, repeats=3)

    df = pd.DataFrame(
        {
            "n": n_vals,
            "LRU Cache Time (s)": lru_times,
            "Splay Tree Time (s)": splay_times,
        }
    )
    print("\nТаблиця часу виконання:\n")
    print(
        df.to_string(
            index=False,
            formatters={
                "LRU Cache Time (s)": lambda x: f"{x:.8f}",
                "Splay Tree Time (s)": lambda x: f"{x:.8f}",
            },
        )
    )

    plt.figure(figsize=(10, 5))
    plt.plot(n_vals, lru_times, marker="o", label="LRU Cache")
    plt.plot(n_vals, splay_times, marker="x", label="Splay Tree")
    plt.title("Порівняння часу виконання для LRU Cache та Splay Tree")
    plt.xlabel("Число Фібоначчі (n)")
    plt.ylabel("Середній час виконання (секунди)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    ratio = [s / l if l else float("inf") for s, l in zip(splay_times, lru_times)]
    worst = max(ratio)
    print(
        f"\nУ середньому обчислення з LRU‑кешем швидше приблизно в {worst:,.0f} раз(ів) для найбільших n.\n"
    )

if __name__ == "__main__":
    main()
