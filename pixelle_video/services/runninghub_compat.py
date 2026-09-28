"""Compatibility layer for RunningHub China API keys and V2 media uploads."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import aiohttp
from comfykit.comfyui.runninghub_client import RunningHubClient
from loguru import logger


RUNNINGHUB_CN_BASE_URL = "https://www.runninghub.cn"
RUNNINGHUB_V2_UPLOAD_ENDPOINT = "/openapi/v2/media/upload/binary"


def _mask_secret(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    return f"***{text[-6:]}" if len(text) > 6 else "***"


def redact_comfykit_config(config: dict) -> dict:
    """Return a shallow copy safe for logs."""
    redacted = dict(config)
    for key in ("api_key", "runninghub_api_key"):
        if key in redacted:
            redacted[key] = _mask_secret(redacted[key])
    return redacted


class RunningHubV2Client(RunningHubClient):
    """Use the China endpoint and the Bearer-authenticated V2 upload API."""

    upload_endpoint = RUNNINGHUB_V2_UPLOAD_ENDPOINT

    def __init__(self, api_key: str = None, base_url: str = None, **kwargs):
        configured_base_url = (
            base_url or os.getenv("RUNNINGHUB_BASE_URL") or RUNNINGHUB_CN_BASE_URL
        )
        super().__init__(api_key=api_key, base_url=configured_base_url, **kwargs)

    async def _upload_once(self, file_path: Path) -> dict:
        session = await self._get_session()
        form = aiohttp.FormData()
        form.add_field(
            "file",
            file_path.read_bytes(),
            filename=file_path.name,
            content_type="application/octet-stream",
        )
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with session.post(
            f"{self.base_url}{self.upload_endpoint}", headers=headers, data=form
        ) as response:
            response_text = await response.text()
            try:
                payload = json.loads(response_text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"RunningHub upload returned non-JSON response (HTTP {response.status})"
                ) from exc

            if response.status != 200 or payload.get("code") != 0:
                message = payload.get("msg") or payload.get("message") or "unknown error"
                raise RuntimeError(f"RunningHub V2 upload failed: {message}")
            return payload

    async def upload_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        last_error: Exception | None = None
        for attempt in range(self.retry_count + 1):
            try:
                payload = await self._upload_once(path)
                file_name = (payload.get("data") or {}).get("fileName")
                if not file_name:
                    raise RuntimeError("RunningHub V2 upload response missing fileName")
                logger.info(f"File uploaded successfully via RunningHub V2: {file_name}")
                return file_name
            except Exception as exc:
                last_error = exc
                if attempt >= self.retry_count:
                    break
                wait_seconds = 2**attempt
                logger.warning(
                    f"RunningHub V2 upload attempt {attempt + 1} failed; "
                    f"retrying in {wait_seconds}s: {exc}"
                )
                await asyncio.sleep(wait_seconds)

        raise RuntimeError(f"RunningHub V2 upload failed after retries: {last_error}") from last_error


def install_runninghub_v2_compat() -> None:
    """Install the client into ComfyKit's executor without patching site-packages."""
    import comfykit.comfyui.runninghub_executor as executor_module

    executor_module.RunningHubClient = RunningHubV2Client
