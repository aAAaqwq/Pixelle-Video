"""
ReelForge - AI-powered book video generator with pluggable capabilities

Convention-based capability system using FastMCP and LiteLLM.

Usage:
    from reelforge import reelforge
    
    # Initialize
    await reelforge.initialize()
    
    # Use capabilities
    answer = await reelforge.llm("Explain atomic habits")
    audio = await reelforge.tts("Hello world")
    book = await reelforge.book_fetcher("原则")
"""

from reelforge.service import ReelForgeCore, reelforge

__version__ = "0.1.0"

__all__ = ["ReelForgeCore", "reelforge"]

