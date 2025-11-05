"""
Frame/Template rendering API schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class FrameRenderRequest(BaseModel):
    """Frame rendering request"""
    template: str = Field(
        ..., 
        description="Template key (e.g., '1080x1920/default.html'). Can also be just filename (e.g., 'default.html') to use default size."
    )
    title: Optional[str] = Field(None, description="Frame title (optional)")
    text: str = Field(..., description="Frame text content")
    image: str = Field(..., description="Image path or URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template": "1080x1920/default.html",
                "title": "Sample Title",
                "text": "This is a sample text for the frame.",
                "image": "resources/example.png"
            }
        }


class FrameRenderResponse(BaseModel):
    """Frame rendering response"""
    success: bool = True
    message: str = "Success"
    frame_path: str = Field(..., description="Path to generated frame image")
    width: int = Field(..., description="Frame width in pixels")
    height: int = Field(..., description="Frame height in pixels")

