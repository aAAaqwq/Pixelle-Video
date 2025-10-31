"""
Prompts package

Centralized prompt management for all LLM interactions.
"""

# Narration prompts
from pixelle_video.prompts.topic_narration import build_topic_narration_prompt
from pixelle_video.prompts.content_narration import build_content_narration_prompt
from pixelle_video.prompts.title_generation import build_title_generation_prompt

# Image prompts
from pixelle_video.prompts.image_generation import (
    build_image_prompt_prompt,
    IMAGE_STYLE_PRESETS,
    DEFAULT_IMAGE_STYLE
)
from pixelle_video.prompts.style_conversion import build_style_conversion_prompt


__all__ = [
    # Narration builders
    "build_topic_narration_prompt",
    "build_content_narration_prompt",
    "build_title_generation_prompt",
    
    # Image builders
    "build_image_prompt_prompt",
    "build_style_conversion_prompt",
    
    # Image style presets
    "IMAGE_STYLE_PRESETS",
    "DEFAULT_IMAGE_STYLE",
]
