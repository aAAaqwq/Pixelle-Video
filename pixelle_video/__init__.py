"""
Pixelle-Video - AI-powered video generator

Convention-based system with unified configuration management.

Usage:
    from pixelle_video import pixelle_video
    
    # Initialize
    await pixelle_video.initialize()
    
    # Use capabilities
    answer = await pixelle_video.llm("Explain atomic habits")
    audio = await pixelle_video.tts("Hello world")
    
    # Generate video
    result = await pixelle_video.generate_video(topic="AI in 2024")
"""

from pixelle_video.service import PixelleVideoCore, pixelle_video
from pixelle_video.config import config_manager

__version__ = "0.1.0"

__all__ = ["PixelleVideoCore", "pixelle_video", "config_manager"]

