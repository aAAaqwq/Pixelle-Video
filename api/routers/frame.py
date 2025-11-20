# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Frame/Template rendering endpoints
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.frame import FrameRenderRequest, FrameRenderResponse
from pixelle_video.services.frame_html import HTMLFrameGenerator
from pixelle_video.utils.template_util import parse_template_size, resolve_template_path

router = APIRouter(prefix="/frame", tags=["Frame Rendering"])


@router.post("/render", response_model=FrameRenderResponse)
async def render_frame(
    request: FrameRenderRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Render a single frame using HTML template
    
    Generates a frame image by combining template, title, text, and image.
    This is useful for previewing templates or generating custom frames.
    
    - **template**: Template key (e.g., '1080x1920/default.html')
    - **title**: Optional title text
    - **text**: Frame text content
    - **image**: Image path (can be local path or URL)
    
    Returns path to generated frame image.
    
    Example:
    ```json
    {
        "template": "1080x1920/modern.html",
        "title": "Welcome",
        "text": "This is a beautiful frame with custom styling",
        "image": "resources/example.png"
    }
    ```
    """
    try:
        logger.info(f"Frame render request: template={request.template}")
        
        # Resolve template path (returns absolute path with "templates/" or "data/templates/" prefix)
        template_path = resolve_template_path(request.template)
        
        # Parse template size
        width, height = parse_template_size(template_path)
        
        # Create HTML frame generator
        generator = HTMLFrameGenerator(template_path)
        
        # Generate frame
        frame_path = await generator.generate_frame(
            title=request.title,
            text=request.text,
            image=request.image
        )
        
        return FrameRenderResponse(
            frame_path=frame_path,
            width=width,
            height=height
        )
        
    except Exception as e:
        logger.error(f"Frame render error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

