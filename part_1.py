from __future__ import annotations

import random
import time
from collections import OrderedDict
from typing import List, Tuple

# 1. LRUCache

class LRUCache:

    def __init__(self, capacity: int = 1_000) -> None:
        self.capacity: int = capacity
        self._cache: OrderedDict[Tuple[int, int], int] = OrderedDict()

    def get(self, key: Tuple[int, int]) -> int:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return -1

    def put(self, key: Tuple[int, int], value: int) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def invalidate_ranges_containing(self, index: int) -> None:
        for key in list(self._cache.keys()):
            left, right = key
            if left <= index <= right:
                del self._cache[key]

# 2. Чотири функції

Array = List[int]


def range_sum_no_cache(array: Array, left: int, right: int) -> int:
    return sum(array[left : right + 1])

def update_no_cache(array: Array, index: int, value: int) -> None:
    array[index] = value

def range_sum_with_cache(
    array: Array, left: int, right: int, cache: LRUCache
) -> int:
    key = (left, right)
    res = cache.get(key)
    if res == -1:
        res = sum(array[left : right + 1])
        cache.put(key, res)
    return res

def update_with_cache(array: Array, index: int, value: int, cache: LRUCache) -> None:
    array[index] = value
    cache.invalidate_ranges_containing(index)

# 3. Генерація запитів

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

# 4. вимірювання часу

def _run_queries(array: Array, queries, use_cache: bool = False) -> float:
    cache = LRUCache(1_000) if use_cache else None
    t0 = time.perf_counter()
    checksum = 0
    for typ, *params in queries:
        if typ == "Range":
            left, right = params
            if cache:
                checksum ^= range_sum_with_cache(array, left, right, cache)
            else:
                checksum ^= range_sum_no_cache(array, left, right)
        else:
            idx, val = params
            if cache:
                update_with_cache(array, idx, val, cache)
            else:
                update_no_cache(array, idx, val)
    time_spent = time.perf_counter() - t0
    return time_spent


def benchmark(n: int = 100_000, q: int = 50_000) -> None:
    base = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    t_no_cache = _run_queries(base.copy(), queries, use_cache=False)

    t_with_cache = _run_queries(base.copy(), queries, use_cache=True)

    speedup = t_no_cache / t_with_cache if t_with_cache else float("inf")
    print(f"Без кешу : {t_no_cache:8.2f} s")
    print(f"LRU‑кеш  : {t_with_cache:8.2f} s  (прискорення ×{speedup:.1f})")


if __name__ == "__main__":
    benchmark()
