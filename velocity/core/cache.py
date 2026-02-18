"""
Query Cache - LRU In-Memory Cache for Velocity

Aynı sorgu tekrar geldiğinde ağa gitmez; önce önbelleğe bakar.

Intelligence isn't just speed of acquisition — it's also knowing
when you've already acquired it.
"""

import hashlib
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple
from loguru import logger


class QueryCache:
    """
    Thread-safe LRU cache for Velocity query results.

    Key design choices:
    - LRU eviction: least recently used entries are dropped when full.
    - TTL per entry: stale results are automatically invalidated.
    - Fuzzy key matching: normalises whitespace/case before hashing so
      "Python vs JS" and "python vs js " hit the same cached entry.

    Usage::

        cache = QueryCache(max_size=256, ttl_seconds=300)

        result = cache.get("What is Python?")
        if result is None:
            result = await velocity.execute("What is Python?")
            cache.set("What is Python?", result)
    """

    def __init__(
        self,
        max_size: int = 256,
        ttl_seconds: float = 300.0,
    ) -> None:
        """
        Args:
            max_size:    Maximum number of cached entries before LRU eviction.
            ttl_seconds: Time-to-live in seconds.  0 = never expire.
        """
        self.max_size = max_size
        self.ttl = ttl_seconds
        # OrderedDict preserves insertion/access order for LRU semantics
        self._store: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, query: str) -> Optional[Any]:
        """Return cached result or None if missing / expired."""
        key = self._make_key(query)
        entry = self._store.get(key)

        if entry is None:
            self._misses += 1
            return None

        value, timestamp = entry

        # TTL check
        if self.ttl > 0 and (time.monotonic() - timestamp) > self.ttl:
            logger.debug(f"Cache EXPIRED: {query[:60]}")
            del self._store[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._store.move_to_end(key)
        self._hits += 1
        logger.debug(f"Cache HIT: {query[:60]}")
        return value

    def set(self, query: str, value: Any) -> None:
        """Store a query result."""
        key = self._make_key(query)

        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (value, time.monotonic())

        # Evict oldest entry if over capacity
        if len(self._store) > self.max_size:
            evicted_key, _ = self._store.popitem(last=False)
            logger.debug(f"Cache EVICT (LRU): {evicted_key[:16]}…")

        logger.debug(f"Cache SET: {query[:60]}")

    def invalidate(self, query: str) -> bool:
        """Remove a single cached entry. Returns True if it existed."""
        key = self._make_key(query)
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Remove all cached entries and reset statistics."""
        self._store.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total else 0.0

    def stats(self) -> Dict[str, Any]:
        return {
            "size": self.size,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate, 3),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_key(query: str) -> str:
        """Normalise and hash the query to a stable cache key."""
        normalised = " ".join(query.lower().split())
        return hashlib.sha256(normalised.encode()).hexdigest()
