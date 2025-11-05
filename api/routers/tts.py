"""
TTS (Text-to-Speech) endpoints
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.tts import TTSSynthesizeRequest, TTSSynthesizeResponse
from pixelle_video.utils.tts_util import get_audio_duration

router = APIRouter(prefix="/tts", tags=["Basic Services"])


@router.post("/synthesize", response_model=TTSSynthesizeResponse)
async def tts_synthesize(
    request: TTSSynthesizeRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Text-to-Speech synthesis endpoint
    
    Convert text to speech audio using ComfyUI workflows.
    
    - **text**: Text to synthesize
    - **workflow**: TTS workflow key (optional, uses default if not specified)
    - **ref_audio**: Reference audio for voice cloning (optional)
    - **voice_id**: (Deprecated) Voice ID for legacy compatibility
    
    Returns path to generated audio file and duration.
    
    Examples:
    ```json
    {
        "text": "Hello, welcome to Pixelle-Video!",
        "workflow": "runninghub/tts_edge.json"
    }
    ```
    
    With voice cloning:
    ```json
    {
        "text": "Hello, this is a cloned voice",
        "workflow": "runninghub/tts_index2.json",
        "ref_audio": "path/to/reference.wav"
    }
    ```
    """
    try:
        logger.info(f"TTS synthesis request: {request.text[:50]}...")
        
        # Build TTS parameters
        tts_params = {"text": request.text}
        
        # Add workflow if specified
        if request.workflow:
            tts_params["workflow"] = request.workflow
        
        # Add ref_audio if specified
        if request.ref_audio:
            tts_params["ref_audio"] = request.ref_audio
        
        # Legacy voice_id support (deprecated)
        if request.voice_id and not request.workflow:
            logger.warning("voice_id parameter is deprecated, please use workflow instead")
            tts_params["voice"] = request.voice_id
        
        # Call TTS service
        audio_path = await pixelle_video.tts(**tts_params)
        
        # Get audio duration
        duration = get_audio_duration(audio_path)
        
        return TTSSynthesizeResponse(
            audio_path=audio_path,
            duration=duration
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

