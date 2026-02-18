"""
Tests for QueryCache
"""

import pytest
import time
from velocity.core.cache import QueryCache


class TestQueryCache:

    def test_miss_on_empty_cache(self):
        cache = QueryCache()
        assert cache.get("anything") is None

    def test_set_and_get(self):
        cache = QueryCache()
        cache.set("What is Python?", {"answer": "a language"})
        result = cache.get("What is Python?")
        assert result == {"answer": "a language"}

    def test_normalisation_case_insensitive(self):
        """Keys should normalise case and whitespace."""
        cache = QueryCache()
        cache.set("What is Python?", "value")
        assert cache.get("WHAT IS PYTHON?") == "value"
        assert cache.get("  what is python?  ") == "value"

    def test_lru_eviction(self):
        """Oldest entry is evicted when max_size is exceeded."""
        cache = QueryCache(max_size=2)
        cache.set("q1", "v1")
        cache.set("q2", "v2")
        cache.set("q3", "v3")  # should evict q1
        assert cache.get("q1") is None
        assert cache.get("q2") == "v2"
        assert cache.get("q3") == "v3"

    def test_lru_access_refreshes_entry(self):
        """Accessing an entry moves it to most-recently-used position."""
        cache = QueryCache(max_size=2)
        cache.set("q1", "v1")
        cache.set("q2", "v2")
        # Access q1 so it becomes MRU
        cache.get("q1")
        # Adding q3 should evict q2 (LRU), not q1
        cache.set("q3", "v3")
        assert cache.get("q1") == "v1"
        assert cache.get("q2") is None
        assert cache.get("q3") == "v3"

    def test_ttl_expiry(self):
        """Entries older than TTL should return None."""
        cache = QueryCache(ttl_seconds=0.05)  # 50 ms TTL
        cache.set("q", "value")
        assert cache.get("q") == "value"
        time.sleep(0.1)
        assert cache.get("q") is None  # expired

    def test_ttl_zero_never_expires(self):
        cache = QueryCache(ttl_seconds=0)
        cache.set("q", "persistent")
        time.sleep(0.05)
        assert cache.get("q") == "persistent"

    def test_invalidate(self):
        cache = QueryCache()
        cache.set("q", "v")
        assert cache.invalidate("q") is True
        assert cache.get("q") is None
        assert cache.invalidate("q") is False  # already gone

    def test_clear(self):
        cache = QueryCache()
        cache.set("q1", "v1")
        cache.set("q2", "v2")
        cache.clear()
        assert cache.size == 0
        assert cache.get("q1") is None

    def test_hit_rate(self):
        cache = QueryCache()
        cache.set("q", "v")
        cache.get("q")   # hit
        cache.get("x")   # miss
        assert cache.hit_rate == pytest.approx(0.5)

    def test_stats_keys(self):
        cache = QueryCache(max_size=10, ttl_seconds=60)
        stats = cache.stats()
        assert "size" in stats
        assert "hit_rate" in stats
        assert "hits" in stats
        assert stats["max_size"] == 10
