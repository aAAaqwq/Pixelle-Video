"""
Image prompt generation service
"""

import json
import re
from typing import List

from loguru import logger

from reelforge.models.storyboard import StoryboardConfig
from reelforge.prompts.image_prompt_template import build_image_prompt_prompt


class ImagePromptGeneratorService:
    """Image prompt generation service"""
    
    def __init__(self, reelforge_core):
        """
        Initialize
        
        Args:
            reelforge_core: ReelForgeCore instance
        """
        self.core = reelforge_core
    
    async def generate_image_prompts(
        self,
        narrations: List[str],
        config: StoryboardConfig,
        image_style_preset: str = None,
        image_style_description: str = None
    ) -> List[str]:
        """
        Generate image prompts based on narrations
        
        Args:
            narrations: List of narrations
            config: Storyboard configuration
            image_style_preset: Preset style name (e.g., "minimal", "futuristic")
            image_style_description: Custom style description (overrides preset)
            
        Returns:
            List of image prompts with style applied
            
        Raises:
            ValueError: If generated prompt count doesn't match narrations
            json.JSONDecodeError: If unable to parse JSON
        """
        logger.info(f"Generating image prompts for {len(narrations)} narrations")
        
        # 1. Build prompt (no style info - generate base scene descriptions)
        prompt = build_image_prompt_prompt(
            narrations=narrations,
            min_words=config.min_image_prompt_words,
            max_words=config.max_image_prompt_words,
            image_style_preset=None,  # Don't include style in LLM prompt
            image_style_description=None
        )
        
        # 2. Call LLM to generate base scene descriptions
        response = await self.core.llm(
            prompt=prompt,
            temperature=0.9,  # Higher temperature for more visual creativity
            max_tokens=2000
        )
        
        logger.debug(f"LLM response: {response[:200]}...")
        
        # 3. Parse JSON
        try:
            result = self._parse_json(response)
            base_prompts = result["image_prompts"]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Response: {response}")
            raise
        except KeyError:
            logger.error("Response missing 'image_prompts' key")
            raise ValueError("Invalid response format")
        
        # 4. Validate count matches narrations
        if len(base_prompts) != len(narrations):
            raise ValueError(
                f"Expected {len(narrations)} image prompts, "
                f"got {len(base_prompts)}"
            )
        
        # 5. Apply style to each prompt using FinalImagePromptService
        from reelforge.services.final_image_prompt import StylePreset
        
        # Convert style preset name to enum if provided
        style_preset_enum = None
        if image_style_preset:
            try:
                style_preset_enum = StylePreset[image_style_preset.upper()]
            except KeyError:
                logger.warning(f"Unknown style preset: {image_style_preset}")
        
        # Apply style to each base prompt
        final_prompts = []
        for base_prompt in base_prompts:
            final_prompt = await self.core.generate_final_image_prompt(
                prompt=base_prompt,
                style_preset=style_preset_enum,
                custom_style_description=image_style_description or ""
            )
            final_prompts.append(final_prompt)
        
        logger.info(f"Generated {len(final_prompts)} final image prompts with style applied")
        return final_prompts
    
    def _parse_json(self, text: str) -> dict:
        """
        Parse JSON from text, with fallback to extract JSON from markdown code blocks
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON dict
        """
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in the text
        json_pattern = r'\{[^{}]*"image_prompts"\s*:\s*\[[^\]]*\][^{}]*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If all fails, raise error
        raise json.JSONDecodeError("No valid JSON found", text, 0)

