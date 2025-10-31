"""
Pixelle-Video Core - Service Layer

Provides unified access to all capabilities (LLM, TTS, Image, etc.)
"""

from typing import Optional

from loguru import logger

from pixelle_video.config import config_manager
from pixelle_video.services.llm_service import LLMService
from pixelle_video.services.tts_service import TTSService
from pixelle_video.services.image import ImageService
from pixelle_video.services.narration_generator import NarrationGeneratorService
from pixelle_video.services.image_prompt_generator import ImagePromptGeneratorService
from pixelle_video.services.title_generator import TitleGeneratorService
from pixelle_video.services.frame_processor import FrameProcessor
from pixelle_video.services.video_generator import VideoGeneratorService


class PixelleVideoCore:
    """
    Pixelle-Video Core - Service Layer
    
    Provides unified access to all capabilities.
    
    Usage:
        from pixelle_video import pixelle_video
        
        # Initialize
        await pixelle_video.initialize()
        
        # Use capabilities directly
        answer = await pixelle_video.llm("Explain atomic habits")
        audio = await pixelle_video.tts("Hello world")
        image = await pixelle_video.image(prompt="a cat")
        
        # Check active capabilities
        print(f"Using LLM: {pixelle_video.llm.active}")
        print(f"Available TTS: {pixelle_video.tts.available}")
    
    Architecture (Simplified):
        PixelleVideoCore (this class)
          ├── config (configuration)
          ├── llm (LLM service - direct OpenAI SDK)
          ├── tts (TTS service - ComfyKit workflows)
          └── image (Image service - ComfyKit workflows)
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize Pixelle-Video Core
        
        Args:
            config_path: Path to configuration file
        """
        # Use global config manager singleton
        self.config = config_manager.config.to_dict()
        self._initialized = False
        
        # Core services (initialized in initialize())
        self.llm: Optional[LLMService] = None
        self.tts: Optional[TTSService] = None
        self.image: Optional[ImageService] = None
        
        # Content generation services
        self.narration_generator: Optional[NarrationGeneratorService] = None
        self.image_prompt_generator: Optional[ImagePromptGeneratorService] = None
        self.title_generator: Optional[TitleGeneratorService] = None
        
        # Frame processing services
        self.frame_processor: Optional[FrameProcessor] = None
        
        # Video generation service (named as verb for direct calling)
        self.generate_video: Optional[VideoGeneratorService] = None
    
    async def initialize(self):
        """
        Initialize core capabilities
        
        This initializes all services and must be called before using any capabilities.
        
        Example:
            await pixelle_video.initialize()
        """
        if self._initialized:
            logger.warning("Pixelle-Video already initialized")
            return
        
        logger.info("🚀 Initializing Pixelle-Video...")
        
        # 1. Initialize core services (no capability layer)
        self.llm = LLMService(self.config)
        self.tts = TTSService(self.config)
        self.image = ImageService(self.config)
        
        # 2. Initialize content generation services
        self.narration_generator = NarrationGeneratorService(self)
        self.image_prompt_generator = ImagePromptGeneratorService(self)
        self.title_generator = TitleGeneratorService(self)
        
        # 3. Initialize frame processing services
        self.frame_processor = FrameProcessor(self)
        
        # 4. Initialize video generation service
        self.generate_video = VideoGeneratorService(self)
        
        self._initialized = True
        logger.info("✅ Pixelle-Video initialized successfully\n")
    
    @property
    def project_name(self) -> str:
        """Get project name from config"""
        return self.config.get("project_name", "Pixelle-Video")
    
    def __repr__(self) -> str:
        """String representation"""
        status = "initialized" if self._initialized else "not initialized"
        return f"<PixelleVideoCore project={self.project_name!r} status={status}>"


# Global instance
pixelle_video = PixelleVideoCore()
