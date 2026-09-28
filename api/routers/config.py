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
Configuration read/write endpoints (2026-08-14, for Super-AIGC admin linkage)

- GET /api/config : return current config (all sensitive keys masked)
- PUT /api/config : deep-merge partial fields into memory + config.yaml
                    (takes effect immediately, no restart needed)
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger

from pixelle_video.config import config_manager

router = APIRouter(tags=["Config"])

# 敏感字段名：GET 回显时统一掩码（api_key / access_key / secret_key 及其带前缀变体）。
_SENSITIVE_KEYS = {"api_key", "access_key", "secret_key"}
_SENSITIVE_SUFFIXES = ("_api_key", "_access_key", "_secret_key", "_secret")


def _is_sensitive_key(key: str) -> bool:
    return key in _SENSITIVE_KEYS or any(key.endswith(suffix) for suffix in _SENSITIVE_SUFFIXES)


def _mask_key(key: Optional[str]) -> str:
    """掩码 API Key：长 key 保留前 3 后 4，短 key 显示「已配置」。"""
    if not key:
        return ""
    return f"{key[:3]}***{key[-4:]}" if len(key) > 8 else "已配置"


def _mask_dict(data: dict) -> dict:
    """递归掩码所有敏感字段，返回新 dict（不修改入参）。"""
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
    """返回当前配置（敏感 key 已掩码），供管理端回显。"""
    return _mask_dict(config_manager.config.model_dump())


@router.put("/config")
async def put_config(body: dict):
    """部分字段更新（deep_merge 语义）：写入内存并落盘 config.yaml，即时生效。

    示例：{"llm": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"}}
    """
    if not isinstance(body, dict) or not body:
        raise HTTPException(status_code=422, detail="请求体必须是非空 JSON 对象")
    try:
        config_manager.update(body)
        config_manager.save()
    except Exception as exc:  # noqa: BLE001 校验失败等统一转 422
        logger.exception("Pixelle 配置更新失败")
        raise HTTPException(status_code=422, detail=f"配置更新失败: {exc}") from exc
    logger.info(f"Pixelle config updated: {sorted(body.keys())}")
    return {"ok": True}
