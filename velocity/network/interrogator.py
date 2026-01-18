"""
Network Interrogator

The network is not storage.
The network is an active epistemological space.

This module interrogates the network in real-time.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
import time


class NetworkInterrogator:
    """
    Network Interrogation System
    
    Executes parallel queries against the network.
    The network is the knowledge base.
    """
    
    def __init__(
        self,
        max_parallel: int = 5,
        timeout: float = 10.0,
        user_agent: str = "Velocity/0.1.0"
    ):
        """
        Initialize Network Interrogator
        
        Args:
            max_parallel: Maximum parallel queries
            timeout: Request timeout in seconds
            user_agent: User agent string
        """
        self.max_parallel = max_parallel
        self.timeout = timeout
        self.user_agent = user_agent
        
        # Statistics
        self.queries_executed = 0
        self.total_latency = 0.0
        self.errors = 0
        
        logger.info(f"Network Interrogator initialized (parallel={max_parallel})")
    
    async def search_parallel(
        self,
        queries: List[str],
        search_engine: str = "duckduckgo"
    ) -> List[Dict[str, Any]]:
        """
        Execute parallel searches across the network.
        
        This is the core of "access-driven" intelligence:
        Speed of interrogation matters more than size of memory.
        
        Args:
            queries: List of search queries
            search_engine: Search engine to use
            
        Returns:
            List of search results
        """
        logger.debug(f"Executing {len(queries)} parallel queries")
        
        # Create tasks for parallel execution
        tasks = [
            self._execute_query(query, search_engine)
            for query in queries[:self.max_parallel]
        ]
        
        # Execute in parallel
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        latency = time.time() - start_time
        
        self.total_latency += latency
        logger.debug(f"Parallel queries completed in {latency:.2f}s")
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Query failed: {result}")
                self.errors += 1
                continue
            processed_results.append(result)
        
        return processed_results
    
    async def _execute_query(
        self,
        query: str,
        search_engine: str
    ) -> Dict[str, Any]:
        """
        Execute a single query.
        
        Args:
            query: Search query
            search_engine: Search engine to use
            
        Returns:
            Query result
        """
        self.queries_executed += 1
        
        try:
            # Try multiple sources in order
            # 1. Wikipedia (best for encyclopedic knowledge)
            try:
                result = await self._query_wikipedia_simple(query)
                if result["success"]:
                    return result
            except Exception as e:
                logger.debug(f"Wikipedia failed: {e}")
            
            # 2. Try DuckDuckGo instant answer
            try:
                result = await self._query_duckduckgo_instant(query)
                if result["success"]:
                    return result
            except Exception as e:
                logger.debug(f"DuckDuckGo instant failed: {e}")
            
            # 3. Fallback to simulated (with better content)
            return await self._simulated_search_enhanced(query)
            
        except Exception as e:
            logger.error(f"All query methods failed: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def _query_duckduckgo(self, query: str) -> Dict[str, Any]:
        """
        Query DuckDuckGo HTML API.
        
        Note: For production, you'd want to use proper API or services.
        This is a demonstration.
        """
        url = "https://html.duckduckgo.com/html/"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    data={"q": query},
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    html = await response.text()
                    content = self._extract_content_from_html(html)
                    
                    return {
                        "success": True,
                        "query": query,
                        "source": "duckduckgo",
                        "content": content,
                        "metadata": {
                            "url": str(response.url),
                            "status": response.status
                        }
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Query timeout: {query}")
                return {
                    "success": False,
                    "query": query,
                    "error": "timeout"
                }
    
    async def _query_wikipedia(self, query: str) -> Dict[str, Any]:
        """
        Query Wikipedia API.
        
        Wikipedia is an excellent knowledge source for Velocity:
        - Always up to date
        - Well-structured
        - Contradictions documented
        """
        url = "https://en.wikipedia.org/w/api.php"
        
        # First try: search for the page
        search_params = {
            "action": "opensearch",
            "format": "json",
            "search": query,
            "limit": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Step 1: Search for matching page
                async with session.get(
                    url,
                    params=search_params,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as search_response:
                    if search_response.status != 200:
                        raise Exception(f"HTTP {search_response.status}")
                    
                    search_data = await search_response.json()
                    
                    # Get the first matching title
                    if not search_data or len(search_data) < 2 or not search_data[1]:
                        raise Exception(f"No Wikipedia page found for: {query}")
                    
                    page_title = search_data[1][0]
                    logger.debug(f"Found Wikipedia page: {page_title}")
                
                # Step 2: Get page content
                content_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "titles": page_title,
                }
                
                async with session.get(
                    url,
                    params=content_params,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", {})
                    
                    # Extract content
                    content = ""
                    page_id = ""
                    for pid, page_data in pages.items():
                        if "extract" in page_data:
                            content = page_data["extract"]
                            page_id = pid
                            break
                    
                    if not content:
                        raise Exception("No content extracted from Wikipedia")
                    
                    logger.info(f"Successfully retrieved Wikipedia content for '{page_title}' ({len(content)} chars)")
                    
                    return {
                        "success": True,
                        "query": query,
                        "source": f"wikipedia:{page_title}",
                        "content": content,
                        "metadata": {
                            "page_id": page_id,
                            "title": page_title,
                            "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                        }
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Wikipedia query timeout: {query}")
                raise Exception("timeout")
            except Exception as e:
                logger.warning(f"Wikipedia query failed for '{query}': {e}")
                raise
    
    async def _query_wikipedia_simple(self, query: str) -> Dict[str, Any]:
        """Simple Wikipedia query without search API"""
        # Clean query - remove command words
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query.replace(' ', '_')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": "Velocity/0.2.0 (Educational Research)"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("extract", "")
                    
                    if content:
                        logger.info(f"Wikipedia SUCCESS: {data.get('title', clean_query)}")
                        return {
                            "success": True,
                            "query": query,
                            "source": f"wikipedia:{data.get('title', clean_query)}",
                            "content": content,
                            "metadata": {
                                "title": data.get("title"),
                                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                            }
                        }
                
                raise Exception(f"HTTP {response.status}")
    
    async def _query_duckduckgo_instant(self, query: str) -> Dict[str, Any]:
        """Query DuckDuckGo Instant Answer API"""
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        url = "https://api.duckduckgo.com/"
        params = {
            "q": clean_query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers={"User-Agent": "Velocity/0.2.0 (Educational Research)"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Try to get content from instant answer
                    content = data.get("AbstractText") or data.get("Abstract")
                    
                    if content and len(content) > 50:
                        logger.info(f"DuckDuckGo SUCCESS: {clean_query}")
                        return {
                            "success": True,
                            "query": query,
                            "source": f"duckduckgo:{data.get('Heading', clean_query)}",
                            "content": content,
                            "metadata": {
                                "heading": data.get("Heading"),
                                "url": data.get("AbstractURL", "")
                            }
                        }
                
                raise Exception(f"No instant answer available")
    
    async def _simulated_search_enhanced(self, query: str) -> Dict[str, Any]:
        """
        Enhanced simulated search with realistic content.
        
        This is a fallback when real APIs fail.
        In production, you'd integrate more APIs or use WebSearch service.
        """
        await asyncio.sleep(0.3)  # Simulate network latency
        
        # Extract topic from query
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        
        # Knowledge base for common queries
        knowledge_base = {
            "python": "Python is a high-level, interpreted programming language created by Guido van Rossum and first released in 1991. It emphasizes code readability with significant whitespace. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "quantum computing": "Quantum computing is a type of computation that uses quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits that can exist in multiple states simultaneously.",
            "artificial intelligence": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction. AI applications include expert systems, natural language processing, speech recognition and machine vision.",
            "machine learning": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
        }
        
        # Try to find matching content
        content = None
        matched_key = None
        query_lower = clean_query.lower()
        
        for key, value in knowledge_base.items():
            if key in query_lower or query_lower in key:
                content = value
                matched_key = key
                break
        
        if not content:
            content = (
                f"Information about {clean_query}:\n\n"
                f"This is enhanced simulated content for Velocity testing. "
                f"In production, this would come from real search APIs, databases, "
                f"and network sources. The Velocity Paradigm emphasizes real-time "
                f"network interrogation rather than pre-trained knowledge storage."
            )
            matched_key = clean_query
        
        logger.info(f"Enhanced simulation: {matched_key}")
        
        return {
            "success": True,
            "query": query,
            "source": f"knowledge_base:{matched_key}",
            "content": content,
            "metadata": {
                "simulated": True,
                "matched_key": matched_key
            }
        }
    
    def _extract_content_from_html(self, html: str) -> str:
        """
        Extract meaningful content from HTML.
        
        Network returns raw HTML. We need to extract signal from noise.
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        
        # Limit length
        return text[:2000]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interrogator statistics"""
        avg_latency = (
            self.total_latency / self.queries_executed
            if self.queries_executed > 0
            else 0.0
        )
        
        return {
            "queries_executed": self.queries_executed,
            "total_latency": round(self.total_latency, 2),
            "avg_latency": round(avg_latency, 3),
            "errors": self.errors,
            "success_rate": (
                (self.queries_executed - self.errors) / self.queries_executed
                if self.queries_executed > 0
                else 0.0
            )
        }
