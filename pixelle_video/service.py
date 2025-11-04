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
from pixelle_video.services.video import VideoService
from pixelle_video.services.narration_generator import NarrationGeneratorService
from pixelle_video.services.image_prompt_generator import ImagePromptGeneratorService
from pixelle_video.services.title_generator import TitleGeneratorService
from pixelle_video.services.frame_processor import FrameProcessor
from pixelle_video.pipelines.standard import StandardPipeline
from pixelle_video.pipelines.custom import CustomPipeline


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
          ├── image (Image service - ComfyKit workflows)
          └── pipelines (video generation pipelines)
              ├── standard (standard workflow)
              ├── custom (custom workflow template)
              └── ... (extensible)
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
        self.video: Optional[VideoService] = None
        
        # Content generation services
        self.narration_generator: Optional[NarrationGeneratorService] = None
        self.image_prompt_generator: Optional[ImagePromptGeneratorService] = None
        self.title_generator: Optional[TitleGeneratorService] = None
        
        # Frame processing services
        self.frame_processor: Optional[FrameProcessor] = None
        
        # Video generation pipelines (dictionary of pipeline_name -> pipeline_instance)
        self.pipelines = {}
        
        # Default pipeline callable (for backward compatibility)
        self.generate_video = None
    
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
        
        # 1. Initialize core services
        self.llm = LLMService(self.config)
        self.tts = TTSService(self.config)
        self.image = ImageService(self.config)
        self.video = VideoService()
        
        # 2. Initialize content generation services
        self.narration_generator = NarrationGeneratorService(self)
        self.image_prompt_generator = ImagePromptGeneratorService(self)
        self.title_generator = TitleGeneratorService(self)
        
        # 3. Initialize frame processing services
        self.frame_processor = FrameProcessor(self)
        
        # 4. Register video generation pipelines
        self.pipelines = {
            "standard": StandardPipeline(self),
            "custom": CustomPipeline(self),
        }
        logger.info(f"📹 Registered pipelines: {', '.join(self.pipelines.keys())}")
        
        # 5. Set default pipeline callable (for backward compatibility)
        self.generate_video = self._create_generate_video_wrapper()
        
        self._initialized = True
        logger.info("✅ Pixelle-Video initialized successfully\n")
    
    def _create_generate_video_wrapper(self):
        """
        Create a wrapper function for generate_video that supports pipeline selection
        
        This maintains backward compatibility while adding pipeline support.
        """
        async def generate_video_wrapper(
            text: str,
            pipeline: str = "standard",
            **kwargs
        ):
            """
            Generate video using specified pipeline
            
            Args:
                text: Input text
                pipeline: Pipeline name ("standard", "book_summary", etc.)
                **kwargs: Pipeline-specific parameters
            
            Returns:
                VideoGenerationResult
            
            Examples:
                # Use standard pipeline (default)
                result = await pixelle_video.generate_video(
                    text="如何提高学习效率",
                    n_scenes=5
                )
                
                # Use custom pipeline
                result = await pixelle_video.generate_video(
                    text=your_content,
                    pipeline="custom",
                    custom_param_example="custom_value"
                )
            """
            if pipeline not in self.pipelines:
                available = ", ".join(self.pipelines.keys())
                raise ValueError(
                    f"Unknown pipeline: '{pipeline}'. "
                    f"Available pipelines: {available}"
                )
            
            pipeline_instance = self.pipelines[pipeline]
            return await pipeline_instance(text=text, **kwargs)
        
        return generate_video_wrapper
    
    @property
    def project_name(self) -> str:
        """Get project name from config"""
        return self.config.get("project_name", "Pixelle-Video")
    
    def __repr__(self) -> str:
        """String representation"""
        status = "initialized" if self._initialized else "not initialized"
        pipelines = f"pipelines={list(self.pipelines.keys())}" if self._initialized else ""
        return f"<PixelleVideoCore project={self.project_name!r} status={status} {pipelines}>"


# Global instance
pixelle_video = PixelleVideoCore()
