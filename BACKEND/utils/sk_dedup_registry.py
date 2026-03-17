"""
Skeleton Key Deduplication Registry
=====================================
Thread-safe registry ensuring no prompt is sent twice across all 3 SK runs.
Shared across the entire attack session as a single instance.
"""

import threading
from typing import Set


class DedupRegistry:
    """Thread-safe registry ensuring no prompt is sent twice across all runs."""

    def __init__(self):
        self._used: Set[str] = set()
        self._lock = threading.Lock()

    def is_used(self, prompt_id: str) -> bool:
        with self._lock:
            return prompt_id in self._used

    def mark_used(self, prompt_id: str):
        with self._lock:
            self._used.add(prompt_id)

    def used_count(self) -> int:
        with self._lock:
            return len(self._used)

    def get_all_used(self) -> set:
        with self._lock:
            return set(self._used)

    def reuse_violations(self, expected_unique: int) -> int:
        """Return how many duplicates were detected (should be 0)."""
        with self._lock:
            return max(0, expected_unique - len(self._used))
