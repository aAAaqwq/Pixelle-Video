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
Digital-human (talking avatar) video generation endpoint.

Wraps pixelle_video.pipelines.digital_human_service.generate_digital_human and
reuses the shared async task manager + file serving:

    POST /api/digital-human/generate/async   -> { task_id }
    GET  /api/tasks/{task_id}                 -> status + result.video_url
    GET  /api/files/<task>/final.mp4          -> the video
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.routers.video import path_to_url
from api.schemas.video import VideoGenerateAsyncResponse
from api.tasks import TaskType, task_manager
from pixelle_video.pipelines.digital_human_service import generate_digital_human

router = APIRouter(prefix="/digital-human", tags=["Digital Human"])

# Uploads land under output/ so the existing /api/files route can serve/clean them
UPLOAD_ROOT = Path("output") / "_dh_uploads"


def _save_upload(file: UploadFile, dest_dir: Path) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "image.png").suffix.lower() or ".png"
    dest = dest_dir / f"{uuid.uuid4().hex[:12]}{suffix}"
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return str(dest.absolute())


@router.post("/generate/async", response_model=VideoGenerateAsyncResponse)
async def generate_digital_human_async(
    pixelle_video: PixelleVideoDep,
    request: Request,
    character: UploadFile = File(..., description="Person/character image"),
    product: Optional[UploadFile] = File(None, description="Product image (required for mode=digital)"),
    mode: str = Form("digital", description="'digital' or 'customize'"),
    goods_title: str = Form("", description="Product title (mode=digital)"),
    goods_text: str = Form("", description="Narration script (required for mode=customize)"),
    tts_voice: str = Form("zh-CN-YunjianNeural"),
    tts_speed: float = Form(1.2),
    tts_inference_mode: str = Form("local"),
):
    """
    Create a digital-human talking video generation task.

    Poll `/api/tasks/{task_id}`; when status is "completed", `result.video_url`
    holds the playable URL.
    """
    if mode not in ("digital", "customize"):
        raise HTTPException(status_code=400, detail="mode must be 'digital' or 'customize'")
    if mode == "digital" and product is None:
        raise HTTPException(status_code=400, detail="product image is required for mode='digital'")
    if mode == "customize" and not goods_text.strip():
        raise HTTPException(status_code=400, detail="goods_text is required for mode='customize'")

    upload_dir = UPLOAD_ROOT / uuid.uuid4().hex[:12]
    try:
        character_path = _save_upload(character, upload_dir)
        product_path = _save_upload(product, upload_dir) if product is not None else None
    except Exception as e:
        logger.error(f"digital-human upload save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploads: {e}")

    task = task_manager.create_task(
        task_type=TaskType.DIGITAL_HUMAN_GENERATION,
        request_params={
            "mode": mode,
            "goods_title": goods_title,
            "tts_voice": tts_voice,
            "tts_speed": tts_speed,
            "tts_inference_mode": tts_inference_mode,
        },
    )

    async def execute() -> dict:
        result = await generate_digital_human(
            pixelle_video,
            mode=mode,
            character_image=character_path,
            product_image=product_path,
            goods_title=goods_title,
            goods_text=goods_text,
            tts_voice=tts_voice,
            tts_speed=tts_speed,
            tts_inference_mode=tts_inference_mode,
        )
        import os

        video_path = result["video_path"]
        file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
        return {
            "video_url": path_to_url(request, video_path),
            "task_id": result["task_id"],
            "script": result["script"],
            "file_size": file_size,
        }

    await task_manager.execute_task(task_id=task.task_id, coro_func=execute)
    logger.info(f"Digital-human async task created: {task.task_id} (mode={mode})")
    return VideoGenerateAsyncResponse(task_id=task.task_id)
