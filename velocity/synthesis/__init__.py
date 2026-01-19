"""
Synthesis Layer - Natural Language Generation

This module provides LLM-powered natural language synthesis
for Velocity's raw factual output.
"""

from .llm_synthesizer import LLMSynthesizer, SynthesisConfig

__all__ = ['LLMSynthesizer', 'SynthesisConfig']
