"""
Title Generator Service

Service for generating video titles from content.
"""

from typing import Literal

from loguru import logger


# Title generation constants
AUTO_LENGTH_THRESHOLD = 15
MAX_TITLE_LENGTH = 15


class TitleGeneratorService:
    """
    Title generation service
    
    Generates video titles from content using different strategies:
    - auto: Automatically decide based on content length
    - direct: Use content directly as title
    - llm: Always use LLM to generate title
    """
    
    def __init__(self, pixelle_video_core):
        """
        Initialize title generator service
        
        Args:
            pixelle_video_core: PixelleVideoCore instance
        """
        self.core = pixelle_video_core
    
    async def __call__(
        self,
        content: str,
        strategy: Literal["auto", "direct", "llm"] = "auto",
        max_length: int = MAX_TITLE_LENGTH
    ) -> str:
        """
        Generate title from content
        
        Args:
            content: Source content (topic or script)
            strategy: Generation strategy
                - "auto": Auto-decide based on content length (default)
                    * If content <= AUTO_LENGTH_THRESHOLD chars: use directly
                    * If content > AUTO_LENGTH_THRESHOLD chars: use LLM
                - "direct": Use content directly (truncated to max_length if needed)
                - "llm": Always use LLM to generate title
            max_length: Maximum title length (default: MAX_TITLE_LENGTH)
        
        Returns:
            Generated title
        
        Examples:
            # Auto strategy (default)
            >>> title = await title_generator("AI技术")  # Short, use directly
            >>> # Returns: "AI技术"
            
            >>> title = await title_generator("如何在信息爆炸时代保持深度思考")  # Long, use LLM
            >>> # Returns: "信息时代的深度思考" (LLM generated)
            
            # Direct strategy
            >>> title = await title_generator("Very long content...", strategy="direct")
            >>> # Returns: "Very long content..." (truncated to max_length)
            
            # LLM strategy
            >>> title = await title_generator("AI", strategy="llm")  # Force LLM even for short content
            >>> # Returns: "人工智能技术" (LLM generated)
        """
        if strategy == "direct":
            return self._use_directly(content, max_length)
        elif strategy == "llm":
            return await self._generate_by_llm(content, max_length)
        else:  # auto
            if len(content.strip()) <= AUTO_LENGTH_THRESHOLD:
                return content.strip()
            return await self._generate_by_llm(content, max_length)
    
    def _use_directly(self, content: str, max_length: int) -> str:
        """
        Use content directly as title (with truncation if needed)
        
        Args:
            content: Source content
            max_length: Maximum title length
            
        Returns:
            Truncated or original content
        """
        content = content.strip()
        if len(content) <= max_length:
            return content
        return content[:max_length]
    
    async def _generate_by_llm(self, content: str, max_length: int) -> str:
        """
        Generate title using LLM
        
        Args:
            content: Source content (topic or script)
            max_length: Maximum title length
            
        Returns:
            LLM-generated title
        """
        from pixelle_video.prompts import build_title_generation_prompt
        
        # Build prompt using template
        prompt = build_title_generation_prompt(content, max_length=500)
        
        # Call LLM to generate title
        response = await self.core.llm(
            prompt=prompt,
            temperature=0.7,
            max_tokens=50
        )
        
        # Clean up response
        title = response.strip()
        
        # Remove quotes if present
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]
        if title.startswith("'") and title.endswith("'"):
            title = title[1:-1]
        
        # Limit to max_length (safety)
        if len(title) > max_length:
            title = title[:max_length]
        
        logger.debug(f"Generated title: '{title}' (length: {len(title)})")
        
        return title

