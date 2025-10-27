"""
Configuration schema with Pydantic models

Single source of truth for all configuration defaults and validation.
"""
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration"""
    api_key: str = Field(default="", description="LLM API Key")
    base_url: str = Field(default="", description="LLM API Base URL")
    model: str = Field(default="", description="LLM Model Name")


class TTSConfig(BaseModel):
    """TTS configuration"""
    default: str = Field(default="edge", description="Default TTS workflow")


class ImageConfig(BaseModel):
    """Image generation configuration"""
    default: str = Field(default="image_default.json", description="Default image workflow")
    comfyui_url: str = Field(default="http://127.0.0.1:8188", description="ComfyUI Server URL")
    runninghub_api_key: str = Field(default="", description="RunningHub API Key (optional)")
    prompt_prefix: str = Field(
        default="Pure white background, minimalist illustration, matchstick figure style, black and white line drawing, simple clean lines",
        description="Prompt prefix for all image generation"
    )


class ReelForgeConfig(BaseModel):
    """ReelForge main configuration"""
    project_name: str = Field(default="ReelForge", description="Project name")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    image: ImageConfig = Field(default_factory=ImageConfig)
    
    def is_llm_configured(self) -> bool:
        """Check if LLM is properly configured"""
        return bool(
            self.llm.api_key and self.llm.api_key.strip() and
            self.llm.base_url and self.llm.base_url.strip() and
            self.llm.model and self.llm.model.strip()
        )
    
    def validate_required(self) -> bool:
        """Validate required configuration"""
        return self.is_llm_configured()
    
    def to_dict(self) -> dict:
        """Convert to dictionary (for backward compatibility)"""
        return self.model_dump()

