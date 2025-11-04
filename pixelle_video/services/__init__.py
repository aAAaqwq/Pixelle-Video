"""
Pixelle-Video Services

Core services providing atomic capabilities.

Core Services (Active):
- LLMService: LLM text generation
- TTSService: Text-to-speech
- ImageService: Image generation
- VideoService: Video processing

Legacy Services (Kept for backward compatibility):
- NarrationGeneratorService: Use pipelines + utils.content_generators instead
- ImagePromptGeneratorService: Use pipelines + utils.content_generators instead
- TitleGeneratorService: Use pipelines + utils.content_generators instead
- FrameProcessor: Use pipelines instead
- VideoGeneratorService: Use pipelines.StandardPipeline instead
"""

from pixelle_video.services.comfy_base_service import ComfyBaseService
from pixelle_video.services.llm_service import LLMService
from pixelle_video.services.tts_service import TTSService
from pixelle_video.services.image import ImageService
from pixelle_video.services.video import VideoService

# Legacy services (kept for backward compatibility)
from pixelle_video.services.narration_generator import NarrationGeneratorService
from pixelle_video.services.image_prompt_generator import ImagePromptGeneratorService
from pixelle_video.services.title_generator import TitleGeneratorService
from pixelle_video.services.frame_processor import FrameProcessor
from pixelle_video.services.video_generator import VideoGeneratorService

__all__ = [
    "ComfyBaseService",
    "LLMService",
    "TTSService",
    "ImageService",
    "VideoService",
    # Legacy (backward compatibility)
    "NarrationGeneratorService",
    "ImagePromptGeneratorService",
    "TitleGeneratorService",
    "FrameProcessor",
    "VideoGeneratorService",
]

