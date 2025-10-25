"""
Frame composer service - Compose image with subtitle overlay

Simple implementation for MVP: adds subtitle text to generated image.
"""

from pathlib import Path

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from reelforge.models.storyboard import StoryboardConfig


class FrameComposerService:
    """
    Frame composer service
    
    Composes final frame image by adding subtitle text to generated image.
    For MVP, we keep it simple - just overlay subtitle at bottom.
    """
    
    def __init__(self):
        self.font_path = self._get_font_path()
    
    def _get_font_path(self) -> str:
        """Get Chinese font path"""
        # Try multiple possible font paths
        possible_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS PingFang
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS Heiti
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS Hiragino
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux Noto
        ]
        
        for font in possible_fonts:
            if Path(font).exists():
                logger.debug(f"Using font: {font}")
                return font
        
        logger.warning("No Chinese font found, will use default")
        return None
    
    async def compose_frame(
        self,
        image_path: str,
        subtitle: str,
        output_path: str,
        config: StoryboardConfig
    ) -> str:
        """
        Compose frame image with subtitle overlay
        
        Args:
            image_path: Generated image path
            subtitle: Subtitle text (narration)
            output_path: Output path for composed image
            config: Storyboard configuration
            
        Returns:
            Path to composed image
        """
        logger.debug(f"Composing frame: {output_path}")
        
        # Load generated image
        img = Image.open(image_path)
        
        # Create canvas with target video size
        canvas = Image.new('RGB', (config.video_width, config.video_height), 'white')
        
        # Calculate scaling to fit image in canvas while preserving aspect ratio
        # Leave space at top (100px) and bottom (300px for subtitle)
        max_img_width = config.video_width
        max_img_height = config.video_height - 400  # Reserve space for subtitle
        
        # Calculate aspect-fit scaling
        img_aspect = img.width / img.height
        target_aspect = max_img_width / max_img_height
        
        if img_aspect > target_aspect:
            # Image is wider - fit to width
            new_width = max_img_width
            new_height = int(max_img_width / img_aspect)
        else:
            # Image is taller - fit to height
            new_height = max_img_height
            new_width = int(max_img_height * img_aspect)
        
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Paste image at center-top
        x_offset = (config.video_width - new_width) // 2
        y_offset = 100  # Leave some space at top
        canvas.paste(img_resized, (x_offset, y_offset))
        
        # Add subtitle at bottom
        draw = ImageDraw.Draw(canvas)
        self._draw_subtitle(draw, subtitle, config.video_width, config.video_height)
        
        # Save
        canvas.save(output_path, quality=95)
        logger.debug(f"Frame composed: {output_path}")
        
        return output_path
    
    def _draw_subtitle(
        self,
        draw: ImageDraw.Draw,
        text: str,
        width: int,
        height: int
    ):
        """Draw subtitle text at bottom of canvas"""
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, 40)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load font: {e}, using default")
            font = ImageFont.load_default()
        
        # Wrap text if too long
        max_chars_per_line = 25
        lines = self._wrap_text(text, max_chars_per_line)
        
        # Calculate position (bottom area)
        line_height = 60
        total_height = len(lines) * line_height
        y_start = height - total_height - 150  # 150px from bottom
        
        # Draw each line centered
        for i, line in enumerate(lines):
            # Get text bounding box
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # Draw shadow for better readability
            draw.text((x + 2, y + 2), line, fill='lightgray', font=font)
            # Draw main text
            draw.text((x, y), line, fill='black', font=font)
    
    def _wrap_text(self, text: str, max_chars: int) -> list:
        """Wrap text into multiple lines"""
        if len(text) <= max_chars:
            return [text]
        
        lines = []
        current_line = ""
        
        for char in text:
            if len(current_line) >= max_chars:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
        
        if current_line:
            lines.append(current_line)
        
        return lines

