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
Headless digital-human (talking avatar) generation service.

Extracted from web/pipelines/digital_human.py so the digital-human口播 flow can be
driven by the REST API (api/routers/digital_human.py) without Streamlit.

Implements the RunningHub workflow path (the one configured on the server via
config.yaml `comfyui.runninghub_api_key`):

    digital  : character + product image -> digital_image workflow -> promo image + script
               -> TTS -> digital_combination workflow -> talking video
    customize: character image is the final talking-head, goods_text is the script
               -> TTS -> digital_combination workflow -> talking video

When no explicit script is supplied, the narration is written by the script LLM
following the caller's `content_type` (see CONTENT_TYPES). That choice is
orthogonal to `mode`, which only decides where the talking-head image comes from.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

import httpx
from loguru import logger

from pixelle_video.utils.os_util import create_task_output_dir

# Default RunningHub workflow descriptors (id lives inside the json file)
DEFAULT_DIGITAL_IMAGE_WORKFLOW = "workflows/runninghub/digital_image.json"
DEFAULT_COMBINATION_WORKFLOW = "workflows/runninghub/digital_combination.json"

DOWNLOAD_TIMEOUT_SECONDS = 300.0


@dataclass(frozen=True)
class ContentType:
    """A narration orientation: display label + prompt template for the script LLM."""

    label: str
    prompt: str


# Narration orientations offered to callers. This registry is the single source of
# truth for the taxonomy: the REST layer lists it instead of re-declaring the keys.
CONTENT_TYPES: dict[str, ContentType] = {
    "knowledge": ContentType(
        label="知识传播",
        prompt=(
            "请围绕主题“{subject}”写一段适合数字人口播短视频的中文知识分享文案。"
            "以传递信息为目的：开头用提问或反常识的结论抓住注意力，中间给出一到两个具体依据，"
            "结尾落到一句能被记住的结论。不要使用推销、促销、下单、优惠等带货话术。"
            "控制在120字以内，只输出文案正文。"
        ),
    ),
    "product": ContentType(
        label="带货",
        prompt=(
            "请为商品“{subject}”写一段适合数字人口播短视频的中文推广文案。"
            "要求自然、有吸引力，控制在80字以内，只输出文案正文。"
        ),
    ),
    "general": ContentType(
        label="通用口播",
        prompt=(
            "请围绕主题“{subject}”写一段适合数字人口播短视频的中文口播文案。"
            "要求口语自然、节奏明快、中心明确，控制在100字以内，只输出文案正文。"
        ),
    ),
    "story": ContentType(
        label="情感故事",
        prompt=(
            "请围绕主题“{subject}”写一段适合数字人口播短视频的中文情感故事文案。"
            "要求有具体场景与细节、情绪有起伏，结尾落到一句能引起共鸣的话。"
            "控制在150字以内，只输出文案正文。"
        ),
    ),
}

# 默认不做带货：未指定内容取向时按知识传播生成。
DEFAULT_CONTENT_TYPE = "knowledge"


def _resolve_script_prompt(content_type: str, subject: str) -> str:
    """Render the narration prompt template for a content type."""
    return CONTENT_TYPES[content_type].prompt.format(subject=subject)


async def _select_script(
    goods_text: str,
    content_type: str,
    goods_title: str,
    llm_call: Callable[[str], Awaitable[str]],
) -> str:
    """Pick the narration: an explicit script wins, otherwise generate by content type.

    ``llm_call`` is an async ``str -> str`` invocation of the script LLM. Shared by
    both modes so an explicit/generated script behaves identically for a talking
    head and a product-promo frame.
    """
    if goods_text and goods_text.strip():
        return goods_text.strip()
    if content_type not in CONTENT_TYPES:
        raise ValueError(
            f"Unsupported content_type: {content_type!r} "
            f"(expected one of {', '.join(CONTENT_TYPES)})"
        )
    return (await llm_call(_resolve_script_prompt(content_type, goods_title))).strip()



def _load_workflow_input(workflow_path: str) -> str:
    """Read a workflow json and return the RunningHub workflow_id (or raw json string)."""
    path = Path(workflow_path)
    if not path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("source") == "runninghub" and "workflow_id" in cfg:
        return cfg["workflow_id"]
    return str(cfg)


def _extract_video_url(result: Any) -> Optional[str]:
    """Pull the first video URL out of a ComfyKit result (mirrors the UI pipeline)."""
    if hasattr(result, "videos") and result.videos:
        return result.videos[0]
    if hasattr(result, "outputs") and result.outputs:
        for _node_id, node_output in result.outputs.items():
            if isinstance(node_output, dict) and node_output.get("videos"):
                videos = node_output["videos"]
                if videos:
                    return videos[0]
    return None


def _build_tts_kwargs(
    *,
    text: str,
    output_path: str,
    inference_mode: str,
    tts_voice: Optional[str],
    tts_speed: Optional[float],
    tts_workflow: Optional[str],
    ref_audio: Optional[str],
) -> dict:
    kwargs: dict = {
        "text": text,
        "output_path": output_path,
        "inference_mode": inference_mode,
    }
    if inference_mode == "local":
        kwargs["voice"] = tts_voice
        kwargs["speed"] = tts_speed
    elif inference_mode == "comfyui":
        if tts_workflow:
            kwargs["workflow"] = tts_workflow
        if ref_audio:
            kwargs["ref_audio"] = ref_audio
    return kwargs


async def generate_digital_human(
    pixelle_video: Any,
    *,
    mode: str = "digital",
    content_type: str = DEFAULT_CONTENT_TYPE,
    character_image: str,
    product_image: Optional[str] = None,
    goods_title: str = "",
    goods_text: str = "",
    tts_voice: str = "zh-CN-YunjianNeural",
    tts_speed: float = 1.2,
    tts_inference_mode: str = "local",
    tts_workflow: Optional[str] = None,
    ref_audio: Optional[str] = None,
    digital_image_workflow: str = DEFAULT_DIGITAL_IMAGE_WORKFLOW,
    combination_workflow: str = DEFAULT_COMBINATION_WORKFLOW,
    task_id: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict:
    """
    Generate a digital-human talking video (RunningHub path).

    Args:
        pixelle_video: initialized PixelleVideoCore instance.
        mode: "digital" (synthesize promo image from character+product) or
              "customize" (character image is already the talking-head).
        content_type: narration orientation used when no script is supplied, one of
                      CONTENT_TYPES ("knowledge" | "product" | "general" | "story").
                      Defaults to knowledge, i.e. not a product pitch.
        character_image: local path to the person/character image.
        product_image: local path to the product image (required for mode="digital").
        goods_title: product title for content_type="product"; for every other
                     content_type it is the narration topic. Also the `goodstype`
                     synthesis input for mode="digital".
        goods_text: explicit narration script. Optional for both modes: when empty,
                    the narration is generated from the content_type template.
        tts_*: voice synthesis options.
        digital_image_workflow / combination_workflow: RunningHub workflow json paths.
        task_id: optional pre-allocated task id (a new output dir is created).
        progress_callback: optional callable (percent:int, message:str).

    Returns:
        dict with keys: video_path, task_id, script, image_url.
    """

    def _progress(pct: int, msg: str) -> None:
        if progress_callback:
            try:
                progress_callback(pct, msg)
            except Exception:  # progress reporting must never break generation
                logger.warning("progress_callback raised; ignoring")

    if mode not in ("digital", "customize"):
        raise ValueError(f"Unsupported mode: {mode!r} (expected 'digital' or 'customize')")
    if content_type not in CONTENT_TYPES:
        raise ValueError(
            f"Unsupported content_type: {content_type!r} "
            f"(expected one of {', '.join(CONTENT_TYPES)})"
        )

    task_dir, task_id = create_task_output_dir(task_id)
    logger.info(
        f"[digital_human] task={task_id} mode={mode} content_type={content_type} dir={task_dir}"
    )

    kit = await pixelle_video._get_or_create_comfykit()
    audio_path = os.path.join(task_dir, "narration.mp3")

    # ---- Step 1: resolve talking-head image + narration script ----
    _progress(10, "preparing")
    if mode == "customize":
        # Talking head is the input image; narration is explicit or generated by
        # content_type. goods_text is optional — without a product image the caller
        # relies on content_type, so customization no longer forces a pitch.
        generated_image_url = character_image
        script = await _select_script(
            goods_text,
            content_type,
            goods_title,
            lambda prompt: pixelle_video.llm(prompt=prompt, temperature=0.7, max_tokens=300),
        )
    else:
        if not product_image:
            raise ValueError("product_image is required for mode='digital'")
        _progress(20, "synthesizing image")
        image_workflow_input = _load_workflow_input(digital_image_workflow)
        synthesis = await kit.execute(
            image_workflow_input,
            {
                "firstimage": character_image,
                "secondimage": product_image,
                "goodstype": goods_title,
            },
        )
        if getattr(synthesis, "status", None) != "completed":
            raise RuntimeError(
                f"digital_image workflow failed: {getattr(synthesis, 'msg', 'unknown error')}"
            )
        generated_image_url = getattr(synthesis, "images", [None])[0]
        workflow_script = getattr(synthesis, "texts", [None])[0]
        script = await _select_script(
            goods_text or workflow_script,
            content_type,
            goods_title,
            lambda prompt: pixelle_video.llm(prompt=prompt, temperature=0.7, max_tokens=300),
        )

    if not generated_image_url:
        raise RuntimeError("Failed to obtain a talking-head image")
    if not script or not str(script).strip():
        raise ValueError("No narration script available")

    # ---- Step 2: TTS ----
    _progress(45, "synthesizing audio")
    await pixelle_video.tts(
        **_build_tts_kwargs(
            text=script,
            output_path=audio_path,
            inference_mode=tts_inference_mode,
            tts_voice=tts_voice,
            tts_speed=tts_speed,
            tts_workflow=tts_workflow,
            ref_audio=ref_audio,
        )
    )

    # ---- Step 3: combine image + audio -> talking video ----
    _progress(65, "synthesizing video")
    combination_input = _load_workflow_input(combination_workflow)
    combination = await kit.execute(
        combination_input,
        {"videoimage": generated_image_url, "audio": audio_path},
    )
    video_url = _extract_video_url(combination)
    if not video_url:
        raise RuntimeError(
            "combination workflow did not return a video; check the workflow configuration"
        )

    # ---- Download final video ----
    _progress(90, "downloading")
    final_video_path = os.path.join(task_dir, "final.mp4")
    async with httpx.AsyncClient(timeout=httpx.Timeout(DOWNLOAD_TIMEOUT_SECONDS)) as client:
        response = await client.get(video_url)
        response.raise_for_status()
        with open(final_video_path, "wb") as f:
            f.write(response.content)

    _progress(100, "done")
    logger.info(f"[digital_human] task={task_id} completed -> {final_video_path}")
    return {
        "video_path": final_video_path,
        "task_id": task_id,
        "script": script,
        "image_url": generated_image_url,
    }
