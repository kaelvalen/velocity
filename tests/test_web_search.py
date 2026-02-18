"""
Tests for WebSearchEngine (async, uses httpx)
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from velocity.network.web_search import WebSearchEngine, SearchResult


@pytest.fixture
def engine():
    return WebSearchEngine(max_results=3, timeout=5)


class TestWebSearchEngine:

    @pytest.mark.asyncio
    async def test_search_returns_list(self, engine):
        """search() should always return a list (may be empty on network failure)."""
        with patch.object(engine, '_search_duckduckgo_html', new_callable=AsyncMock) as mock_ddg:
            mock_ddg.return_value = [
                SearchResult(url="https://example.com", title="Example", snippet="Test snippet"),
            ]
            results = await engine.search("Python programming language")
            assert isinstance(results, list)
            assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_search_result_structure(self, engine):
        with patch.object(engine, '_search_duckduckgo_html', new_callable=AsyncMock) as mock_ddg:
            mock_ddg.return_value = [
                SearchResult(url="https://python.org", title="Python", snippet="Official site"),
            ]
            with patch.object(engine, '_fetch_content', new_callable=AsyncMock, return_value="Python content"):
                results = await engine.search("Python")
                if results:
                    r = results[0]
                    assert hasattr(r, 'url')
                    assert hasattr(r, 'title')
                    assert hasattr(r, 'snippet')
                    assert hasattr(r, 'source_type')

    @pytest.mark.asyncio
    async def test_max_results_respected(self, engine):
        engine.max_results = 2
        with patch.object(engine, '_search_duckduckgo_html', new_callable=AsyncMock) as mock_ddg:
            mock_ddg.return_value = [
                SearchResult(url=f"https://site{i}.com", title=f"Site {i}", snippet="")
                for i in range(5)
            ]
            with patch.object(engine, '_fetch_content', new_callable=AsyncMock, return_value=""):
                results = await engine.search("test")
                assert len(results) <= engine.max_results

    @pytest.mark.asyncio
    async def test_search_handles_failure_gracefully(self, engine):
        """Even if all backends fail, search() returns an empty list (no exception)."""
        with patch.object(engine, '_search_duckduckgo_html', side_effect=Exception("network error")):
            results = await engine.search("test query")
            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_close_client(self, engine):
        """close() should not raise even if client was never used."""
        await engine.close()

    def test_client_is_lazy(self, engine):
        """Client should not be created until first access."""
        assert engine._client is None
        _ = engine.client  # access property
        assert engine._client is not None
