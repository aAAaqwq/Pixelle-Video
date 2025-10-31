"""
FastAPI Dependencies

Provides dependency injection for PixelleVideoCore and other services.
"""

from typing import Annotated
from fastapi import Depends
from loguru import logger

from pixelle_video.service import PixelleVideoCore


# Global Pixelle-Video instance
_pixelle_video_instance: PixelleVideoCore = None


async def get_pixelle_video() -> PixelleVideoCore:
    """
    Get Pixelle-Video core instance (dependency injection)
    
    Returns:
        PixelleVideoCore instance
    """
    global _pixelle_video_instance
    
    if _pixelle_video_instance is None:
        _pixelle_video_instance = PixelleVideoCore()
        await _pixelle_video_instance.initialize()
        logger.info("✅ Pixelle-Video initialized for API")
    
    return _pixelle_video_instance


async def shutdown_pixelle_video():
    """Shutdown Pixelle-Video instance"""
    global _pixelle_video_instance
    if _pixelle_video_instance:
        logger.info("Shutting down Pixelle-Video...")
        _pixelle_video_instance = None


# Type alias for dependency injection
PixelleVideoDep = Annotated[PixelleVideoCore, Depends(get_pixelle_video)]

