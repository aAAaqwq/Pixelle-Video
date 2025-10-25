"""
TTS (Text-to-Speech) Service
"""

import base64
import uuid
from typing import Optional

from reelforge.services.base import BaseService
from reelforge.utils.os_util import get_temp_path, save_bytes_to_file


class TTSService(BaseService):
    """
    TTS (Text-to-Speech) service
    
    Provides unified access to various TTS providers (Edge TTS, Azure TTS, etc.)
    Returns path to saved audio file.
    
    Usage:
        # Direct call (auto-generate temp path)
        audio_path = await reelforge.tts("Hello world")
        # Returns: "temp/abc123def456.mp3"
        
        # With voice parameter
        audio_path = await reelforge.tts(
            text="你好，世界",
            voice="zh-CN-YunjianNeural"
        )
        
        # Specify custom output path
        audio_path = await reelforge.tts(
            text="Hello",
            output_path="output/greeting.mp3"
        )
        
        # Check active TTS
        print(f"Using: {reelforge.tts.active}")
    """
    
    def __init__(self, router):
        super().__init__(router, "tts")
    
    async def __call__(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (uses default if not specified)
            rate: Speech rate (e.g., "+0%", "+50%", "-20%")
            output_path: Output file path (default: temp/<uuid>.mp3)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Path to saved audio file (str)
        
        Example:
            # Auto-generate path
            audio_path = await reelforge.tts("Hello world")
            # Returns: "temp/abc123def456.mp3"
            
            # Specify custom path
            audio_path = await reelforge.tts(
                "你好，世界",
                voice="zh-CN-YunjianNeural",
                output_path="output/greeting.mp3"
            )
        """
        params = {"text": text}
        if voice is not None:
            params["voice"] = voice
        if rate is not None:
            params["rate"] = rate
        params.update(kwargs)
        
        # Call capability and get base64-encoded audio
        audio_base64 = await self._config_manager.call(self._capability_type, **params)
        
        # Decode base64 to bytes
        if isinstance(audio_base64, str):
            audio_data = base64.b64decode(audio_base64)
        else:
            audio_data = audio_base64
        
        # Generate output path if not specified
        if output_path is None:
            # Generate UUID without hyphens for filename
            file_uuid = uuid.uuid4().hex
            output_path = get_temp_path(f"{file_uuid}.mp3")
        
        # Save to file
        saved_path = save_bytes_to_file(audio_data, output_path)
        
        return saved_path

