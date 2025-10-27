"""
ReelForge - AI-powered video generator

Convention-based system with unified configuration management.

Usage:
    from reelforge import reelforge
    
    # Initialize
    await reelforge.initialize()
    
    # Use capabilities
    answer = await reelforge.llm("Explain atomic habits")
    audio = await reelforge.tts("Hello world")
    
    # Generate video
    result = await reelforge.generate_video(topic="AI in 2024")
"""

from reelforge.service import ReelForgeCore, reelforge
from reelforge.config import config_manager

__version__ = "0.1.0"

__all__ = ["ReelForgeCore", "reelforge", "config_manager"]

