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
Configuration read/write endpoints.

- GET /api/config : return the current configuration (sensitive keys masked)
- PUT /api/config : deep-merge partial fields into memory + config.yaml
                    (takes effect immediately, no restart required)

Added for the Super-AIGC admin linkage (2026-08-14): the Super-AIGC admin
panel writes Pixelle service parameters through these endpoints, so that
"changing the global model config" equals "changing the Pixelle service
configuration".
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger

from pixelle_video.config import config_manager

router = APIRouter(tags=["Config"])

# Sensitive field names masked in GET responses.
_SENSITIVE_KEYS = {"api_key", "access_key", "secret_key"}
_SENSITIVE_SUFFIXES = ("_api_key", "_access_key", "_secret_key", "_secret")


def _is_sensitive_key(key: str) -> bool:
    """Whether the field name carries a credential value."""
    return key in _SENSITIVE_KEYS or any(
        key.endswith(suffix) for suffix in _SENSITIVE_SUFFIXES
    )


def _mask_key(key: Optional[str]) -> str:
    """Mask an API key: keep first 3 / last 4 chars for long keys, else "configured"."""
    if not key:
        return ""
    return f"{key[:3]}***{key[-4:]}" if len(key) > 8 else "configured"


def _mask_dict(data: dict) -> dict:
    """Recursively mask sensitive values; returns a new dict (input untouched)."""
    out = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out[key] = _mask_dict(value)
        elif _is_sensitive_key(key) and isinstance(value, str) and value:
            out[key] = _mask_key(value)
        else:
            out[key] = value
    return out


@router.get("/config")
async def get_config():
    """Return the current configuration with sensitive keys masked."""
    return _mask_dict(config_manager.config.model_dump())


@router.put("/config")
async def put_config(body: dict):
    """Deep-merge partial fields into memory + config.yaml (takes effect immediately).

    Example: {"llm": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"}}
    """
    if not isinstance(body, dict) or not body:
        raise HTTPException(
            status_code=422, detail="Request body must be a non-empty JSON object"
        )
    try:
        config_manager.update(body)
        config_manager.save()
    except Exception as exc:  # noqa: BLE001 - validation errors are surfaced as 422
        logger.exception("Failed to update Pixelle configuration")
        raise HTTPException(
            status_code=422, detail=f"Configuration update failed: {exc}"
        ) from exc
    logger.info(f"Pixelle config updated: {sorted(body.keys())}")
    return {"ok": True}
