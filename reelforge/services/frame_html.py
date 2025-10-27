"""
HTML-based Frame Generator Service

Renders HTML templates to frame images with variable substitution

Linux Environment Requirements:
    - fontconfig package must be installed
    - Basic fonts (e.g., fonts-liberation, fonts-noto) recommended
    
    Ubuntu/Debian: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk
    CentOS/RHEL: sudo yum install -y fontconfig liberation-fonts google-noto-cjk-fonts
"""

import os
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from html2image import Html2Image
from loguru import logger


class HTMLFrameGenerator:
    """
    HTML-based frame generator
    
    Renders HTML templates to frame images with variable substitution.
    Users can create custom templates using any HTML/CSS.
    
    Usage:
        >>> generator = HTMLFrameGenerator("templates/modern.html")
        >>> frame_path = await generator.generate_frame(
        ...     topic="Why reading matters",
        ...     text="Reading builds new neural pathways...",
        ...     image="/path/to/image.png",
        ...     ext={"content_title": "Sample Title", "content_author": "Author Name"}
        ... )
    """
    
    def __init__(self, template_path: str):
        """
        Initialize HTML frame generator
        
        Args:
            template_path: Path to HTML template file
        """
        self.template_path = template_path
        self.template = self._load_template(template_path)
        self.hti = None  # Lazy init to avoid overhead
        self._check_linux_dependencies()
        logger.debug(f"Loaded HTML template: {template_path}")
    
    def _check_linux_dependencies(self):
        """Check Linux system dependencies and warn if missing"""
        if os.name != 'posix':
            return
        
        try:
            import subprocess
            
            # Check fontconfig
            result = subprocess.run(
                ['fc-list'], 
                capture_output=True, 
                timeout=2
            )
            
            if result.returncode != 0:
                logger.warning(
                    "⚠️  fontconfig not found or not working properly. "
                    "Install with: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk"
                )
            elif not result.stdout:
                logger.warning(
                    "⚠️  No fonts detected by fontconfig. "
                    "Install fonts with: sudo apt-get install -y fonts-liberation fonts-noto-cjk"
                )
            else:
                logger.debug(f"✓ Fontconfig detected {len(result.stdout.splitlines())} fonts")
                
        except FileNotFoundError:
            logger.warning(
                "⚠️  fontconfig (fc-list) not found on system. "
                "Install with: sudo apt-get install -y fontconfig"
            )
        except Exception as e:
            logger.debug(f"Could not check fontconfig status: {e}")
    
    def _load_template(self, template_path: str) -> str:
        """Load HTML template from file"""
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"Template loaded: {len(content)} chars")
        return content
    
    def _ensure_hti(self, width: int, height: int):
        """Lazily initialize Html2Image instance"""
        if self.hti is None:
            # Configure Chrome flags for Linux headless environment
            custom_flags = [
                '--no-sandbox',  # Bypass AppArmor/sandbox restrictions
                '--disable-dev-shm-usage',  # Avoid shared memory issues
                '--disable-gpu',  # Disable GPU acceleration
                '--disable-software-rasterizer',  # Disable software rasterizer
                '--disable-extensions',  # Disable extensions
                '--disable-setuid-sandbox',  # Additional sandbox bypass
                '--disable-dbus',  # Disable DBus to avoid permission errors
                '--hide-scrollbars',  # Hide scrollbars for cleaner output
                '--mute-audio',  # Mute audio
                '--disable-background-networking',  # Disable background networking
                '--disable-features=TranslateUI',  # Disable translate UI
                '--disable-ipc-flooding-protection',  # Improve performance
                '--no-first-run',  # Skip first run dialogs
                '--no-default-browser-check',  # Skip default browser check
                '--disable-backgrounding-occluded-windows',  # Improve performance
                '--disable-renderer-backgrounding',  # Improve performance
            ]
            
            self.hti = Html2Image(
                size=(width, height),
                custom_flags=custom_flags
            )
            logger.debug(f"Initialized Html2Image with size ({width}, {height}) and {len(custom_flags)} custom flags")
    
    async def generate_frame(
        self,
        topic: str,
        text: str,
        image: str,
        ext: Optional[Dict[str, Any]] = None,
        width: int = 1080,
        height: int = 1920
    ) -> str:
        """
        Generate frame from HTML template
        
        Args:
            topic: Video topic/theme
            text: Narration text for this frame
            image: Path to AI-generated image
            ext: Additional data (content_title, content_author, etc.)
            width: Frame width in pixels
            height: Frame height in pixels
        
        Returns:
            Path to generated frame image
        """
        # Build variable context
        context = {
            # Required variables
            "topic": topic,
            "text": text,
            "image": image,
        }
        
        # Add all ext fields
        if ext:
            context.update(ext)
        
        # Replace variables in HTML
        html = self.template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value) if value is not None else "")
        
        # Generate unique output path
        from reelforge.utils.os_util import get_output_path
        output_filename = f"frame_{uuid.uuid4().hex[:16]}.png"
        output_path = get_output_path(output_filename)
        
        # Ensure Html2Image is initialized
        self._ensure_hti(width, height)
        
        # Render HTML to image
        logger.debug(f"Rendering HTML template to {output_path}")
        try:
            self.hti.screenshot(
                html_str=html,
                save_as=output_filename,
                size=(width, height)
            )
            
            # html2image saves to current directory by default, move to output
            import os
            import shutil
            if os.path.exists(output_filename):
                shutil.move(output_filename, output_path)
            
            logger.info(f"✅ Frame generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to render HTML template: {e}")
            raise RuntimeError(f"HTML rendering failed: {e}")

