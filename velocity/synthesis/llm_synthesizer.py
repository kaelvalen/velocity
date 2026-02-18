"""
LLM Synthesizer - Natural Language Generation Layer

Transforms Velocity's raw factual output into natural, fluent text
using lightweight LLMs (Ollama, Groq, or local models).

Architecture:
    Velocity (NNEI) → Raw Facts → LLM Synthesis → Natural Answer
    
Preserves NNEI paradigm: LLM used ONLY for formatting, not facts.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

import httpx
from loguru import logger


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"           # Local, privacy-first
    GROQ = "groq"               # Fast cloud API
    OPENAI = "openai"           # OpenAI API
    ANTHROPIC = "anthropic"     # Anthropic Claude
    NONE = "none"               # Fallback: no LLM synthesis


@dataclass
class SynthesisConfig:
    """Configuration for LLM synthesis"""
    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = "mistral:7b"  # Default: Mistral 7B via Ollama
    temperature: float = 0.3    # Low temp = more factual
    max_tokens: int = 500
    timeout: int = 30
    stream: bool = False        # Enable server-sent streaming

    # API keys (loaded from env if not set)
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    
    # Fallback behavior
    fallback_to_raw: bool = True  # If LLM fails, return raw


class LLMSynthesizer:
    """
    LLM-powered synthesis layer for natural language generation.
    
    Workflow:
        1. Velocity gathers raw facts (NNEI)
        2. LLMSynthesizer formats into natural text
        3. Output preserves sources and confidence from Velocity
    
    Example:
        synthesizer = LLMSynthesizer(config)
        natural_answer = await synthesizer.synthesize(
            raw_facts="Python is a programming language...",
            sources=["python.org", "wikipedia.org"],
            query="What is Python?"
        )
    """
    
    def __init__(self, config: Optional[SynthesisConfig] = None):
        self.config = config or SynthesisConfig()
        
        # Load API keys from environment
        if not self.config.groq_api_key:
            self.config.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.config.openai_api_key:
            self.config.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.config.anthropic_api_key:
            self.config.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        
        logger.info(f"LLM Synthesizer initialized: {self.config.provider.value}")
    
    async def synthesize(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Synthesize raw facts into natural language.
        
        Args:
            raw_facts: Raw factual content from Velocity
            sources: List of source URLs
            query: Original user query
            language: Target language (auto-detect or specify)
        
        Returns:
            {
                'natural_answer': str,  # Fluent, natural text
                'provider': str,        # Which LLM was used
                'success': bool,        # Synthesis successful
                'fallback': bool        # Whether fallback was used
            }
        """
        
        # Check if LLM synthesis is disabled
        if self.config.provider == LLMProvider.NONE:
            return {
                'natural_answer': raw_facts,
                'provider': 'none',
                'success': True,
                'fallback': True
            }
        
        try:
            # Try primary provider
            if self.config.provider == LLMProvider.OLLAMA:
                result = await self._synthesize_ollama(raw_facts, sources, query, language)
            elif self.config.provider == LLMProvider.GROQ:
                result = await self._synthesize_groq(raw_facts, sources, query, language)
            elif self.config.provider == LLMProvider.OPENAI:
                result = await self._synthesize_openai(raw_facts, sources, query, language)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                result = await self._synthesize_anthropic(raw_facts, sources, query, language)
            else:
                raise ValueError(f"Unknown provider: {self.config.provider}")
            
            return {
                'natural_answer': result,
                'provider': self.config.provider.value,
                'success': True,
                'fallback': False
            }
        
        except Exception as e:
            logger.warning(f"LLM synthesis failed: {e}")
            
            # Fallback to raw if configured
            if self.config.fallback_to_raw:
                return {
                    'natural_answer': raw_facts,
                    'provider': 'fallback',
                    'success': False,
                    'fallback': True
                }
            else:
                raise
    
    async def _synthesize_ollama(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str
    ) -> str:
        """Synthesize using Ollama (local)"""
        
        # Build prompt
        prompt = self._build_synthesis_prompt(raw_facts, sources, query, language)
        
        # Call Ollama API
        url = f"{self.config.ollama_host}/api/generate"
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": self.config.temperature,
            "stream": self.config.stream,
            "options": {
                "num_predict": self.config.max_tokens,
                "stop": ["</s>", "<|im_end|>"]  # Common stop tokens
            }
        }
        
        if self.config.stream:
            return await self._stream_ollama(url, payload)

        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        generated = result.get('response', '').strip()
        
        # If empty, return raw facts (fallback)
        if not generated or len(generated) < 10:
            logger.warning(f"Ollama returned empty/short response, using raw facts")
            return raw_facts
        
        return generated

    async def _stream_ollama(self, url: str, payload: dict) -> str:
        """Stream tokens from Ollama and collect into a single string."""
        collected: List[str] = []
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                import json as _json
                try:
                    chunk = _json.loads(line)
                    token = chunk.get("response", "")
                    collected.append(token)
                    if chunk.get("done"):
                        break
                except Exception:
                    continue
        text = "".join(collected).strip()
        return text if len(text) >= 10 else "".join(collected)
    
    async def _synthesize_groq(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str
    ) -> str:
        """Synthesize using Groq (cloud, fast)"""
        
        if not self.config.groq_api_key:
            raise ValueError("Groq API key not configured")
        
        # Build prompt
        prompt = self._build_synthesis_prompt(raw_facts, sources, query, language)
        
        # Call Groq API
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.model,  # e.g., "mixtral-8x7b-32768"
            "messages": [
                {
                    "role": "system",
                    "content": "You are a synthesis assistant. Transform raw facts into natural, fluent text. Preserve all factual content. Be concise and clear."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": self.config.stream,
        }

        if self.config.stream:
            return await self._stream_openai_compatible(url, payload, headers)

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    async def _synthesize_openai(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str
    ) -> str:
        """Synthesize using OpenAI Chat Completions API."""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key not configured (set OPENAI_API_KEY)")

        prompt = self._build_synthesis_prompt(raw_facts, sources, query, language)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.config.model,  # e.g. "gpt-4o-mini"
            "messages": [
                {
                    "role": "system",
                    "content": "You are a synthesis assistant. Rewrite raw facts in natural, concise language. Preserve all factual content.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": self.config.stream,
        }

        if self.config.stream:
            return await self._stream_openai_compatible(url, payload, headers)

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    async def _synthesize_anthropic(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str
    ) -> str:
        """Synthesize using Anthropic Messages API."""
        if not self.config.anthropic_api_key:
            raise ValueError("Anthropic API key not configured (set ANTHROPIC_API_KEY)")

        prompt = self._build_synthesis_prompt(raw_facts, sources, query, language)

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.config.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.config.model,  # e.g. "claude-3-haiku-20240307"
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": self.config.stream,
            "system": "You are a synthesis assistant. Rewrite raw facts in natural, concise language. Preserve all factual content.",
            "messages": [{"role": "user", "content": prompt}],
        }

        if self.config.stream:
            return await self._stream_anthropic(url, payload, headers)

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()

    # ------------------------------------------------------------------
    # Streaming helpers
    # ------------------------------------------------------------------

    async def _stream_openai_compatible(
        self,
        url: str,
        payload: dict,
        headers: dict
    ) -> str:
        """Stream tokens from any OpenAI-compatible endpoint (OpenAI, Groq)."""
        import json as _json
        collected: List[str] = []
        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                try:
                    chunk = _json.loads(line)
                    token = chunk["choices"][0]["delta"].get("content", "")
                    collected.append(token)
                except Exception:
                    continue
        return "".join(collected).strip()

    async def _stream_anthropic(
        self,
        url: str,
        payload: dict,
        headers: dict
    ) -> str:
        """Stream tokens from Anthropic streaming API."""
        import json as _json
        collected: List[str] = []
        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                try:
                    chunk = _json.loads(line)
                    if chunk.get("type") == "content_block_delta":
                        token = chunk.get("delta", {}).get("text", "")
                        collected.append(token)
                except Exception:
                    continue
        return "".join(collected).strip()
    
    def _build_synthesis_prompt(
        self,
        raw_facts: str,
        sources: List[str],
        query: str,
        language: str
    ) -> str:
        """Build prompt for LLM synthesis"""
        
        # Auto-detect language if needed
        if language == "auto":
            # Simple language detection from query
            if any(ord(c) > 127 for c in query):  # Non-ASCII chars
                language = "the same language as the query"
            else:
                language = "English"
        
        # Format sources
        sources_text = ", ".join(sources[:3]) if sources else "web sources"
        
        # Simpler, more direct prompt (works better with Qwen)
        prompt = f"""You are a helpful assistant. Rewrite the following information in natural, fluent language.

User asked: {query}

Information:
{raw_facts[:500]}

Instructions:
- Write 2-3 clear sentences in {language}
- Keep all facts accurate
- Be natural and conversational
- Don't mention sources

Answer:"""
        
        return prompt
    
    async def health_check(self) -> bool:
        """Check if LLM provider is available"""
        try:
            if self.config.provider == LLMProvider.OLLAMA:
                response = await self.client.get(f"{self.config.ollama_host}/api/tags")
                return response.status_code == 200
            elif self.config.provider == LLMProvider.GROQ:
                return bool(self.config.groq_api_key)
            elif self.config.provider == LLMProvider.OPENAI:
                return bool(self.config.openai_api_key)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return bool(self.config.anthropic_api_key)
            else:
                return True  # NONE provider always available
        except:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Convenience function
async def synthesize_with_llm(
    raw_facts: str,
    sources: List[str],
    query: str,
    config: Optional[SynthesisConfig] = None
) -> str:
    """
    Convenience function for one-off synthesis.
    
    Example:
        answer = await synthesize_with_llm(
            raw_facts="Python is...",
            sources=["python.org"],
            query="What is Python?"
        )
    """
    synthesizer = LLMSynthesizer(config)
    try:
        result = await synthesizer.synthesize(raw_facts, sources, query)
        return result['natural_answer']
    finally:
        await synthesizer.close()
