"""Tests for digital-human content_type selection and the product-optional flow.

Two layers:

1. _select_script / _resolve_script_prompt (pipeline layer) — how the narration
   is chosen: an explicit script wins, otherwise it is generated from the
   content_type template; knowledge never surfaces a sales pitch.
2. The REST route — an invalid content_type is a 400, and a customize request
   with NO product image and NO script is now accepted (it used to 400) because
   the engine generates the narration from content_type.

No real DB / network / RunningHub: the PixelleVideo dependency and the task
manager are both replaced so nothing actually runs and uploads are not written.
"""

from __future__ import annotations

import io

import pytest
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient

from api import dependencies as deps
from api.routers import digital_human as router
from pixelle_video.pipelines.digital_human_service import (
    DEFAULT_CONTENT_TYPE,
    _resolve_script_prompt,
    _select_script,
)


# --------------------------------------------------------------------------- #
# _resolve_script_prompt / _select_script (pipeline layer)
# --------------------------------------------------------------------------- #

async def _fake_llm(prompt: str) -> str:
    return f"generated:{prompt}"


class TestResolveScriptPrompt:
    def test_knowledge_default_and_no_pitch(self):
        p = _resolve_script_prompt("knowledge", "手冲咖啡入门")
        assert "知识分享" in p
        assert "请围绕主题“手冲咖啡入门”" in p
        # The prompt only references sales words as a ban ("不要使用推销、促销…").
        # Assert the ban is present and the orientation itself never asks to sell.
        assert "不要使用" in p
        assert "带货话术" in p
        # The subject is a topic, not a product being pitched.
        assert "请为商品" not in p

    def test_product_targets_goods(self):
        p = _resolve_script_prompt("product", "某商品")
        assert "商品“某商品”" in p

    def test_each_type_renders(self):
        for key in ("knowledge", "product", "general", "story"):
            assert _resolve_script_prompt(key, "x")  # must not raise


@pytest.mark.asyncio
class TestSelectScript:
    async def test_explicit_script_wins(self):
        script = await _select_script("  自定义内容  ", "product", "t", _fake_llm)
        assert script == "自定义内容"
        assert not script.startswith("generated:")

    async def test_empty_generates_by_content_type(self):
        script = await _select_script("", "knowledge", "手冲咖啡入门", _fake_llm)
        assert script.startswith("generated:")
        assert "知识分享" in script

    async def test_whitespace_generates(self):
        script = await _select_script("   ", "general", "主题", _fake_llm)
        assert script.startswith("generated:")

    async def test_bad_content_type_raises_when_generating(self):
        with pytest.raises(ValueError):
            await _select_script("", "bogus", "x", _fake_llm)

    async def test_explicit_script_bypasses_content_type_validation(self):
        # An explicit script should not need a valid content_type.
        script = await _select_script("写好的文案", "bogus", "x", _fake_llm)
        assert script == "写好的文案"


# --------------------------------------------------------------------------- #
# REST route: content_type validated, product image is optional in customize
# --------------------------------------------------------------------------- #

class _FakeTask:
    def __init__(self, task_id: str):
        self.task_id = task_id


class _FakeManager:
    """Records the submitted params and never runs the coroutine."""

    def __init__(self):
        self.last_params = None
        self.task = _FakeTask("task-1")

    def create_task(self, task_type, request_params=None):
        self.last_params = request_params or {}
        return self.task

    async def execute_task(self, task_id, coro_func, *args, **kwargs):
        return None


@pytest.fixture
def client(monkeypatch):
    """TestClient with PixelleVideo → stub and task_manager → no-op recorder."""
    app = FastAPI()

    # PixelleVideoDep → get_pixelle_video would initialize the real core. Stub it.
    async def _stub_pixelle():
        return object()

    app.dependency_overrides[deps.get_pixelle_video] = _stub_pixelle

    app.include_router(router.router)

    # Never write uploads to disk.
    def _fake_save(file, dest_dir):
        return "/tmp/fake_face.png"

    monkeypatch.setattr(router, "_save_upload", _fake_save)

    # Replace task_manager in the router module namespace so nothing runs.
    fake_mgr = _FakeManager()
    monkeypatch.setattr(router, "task_manager", fake_mgr)

    with TestClient(app) as c:
        yield c, fake_mgr


def _face() -> dict:
    return {
        "files": {"character": ("face.png", b"fake-image", "application/octet-stream")}
    }


class TestGenerateAsyncValidation:
    def test_invalid_content_type_is_400(self, client):
        c, _ = client
        r = c.post(
            "/digital-human/generate/async",
            data={"mode": "customize", "content_type": "bogus"},
            **_face(),
        )
        assert r.status_code == 400
        assert "content_type" in r.json()["detail"]

    def test_customize_without_script_is_accepted(self, client):
        # Product image is optional: customize without a script used to 400,
        # now the engine generates the narration from content_type.
        c, mgr = client
        r = c.post(
            "/digital-human/generate/async",
            data={"mode": "customize", "content_type": "knowledge", "goods_title": "手冲咖啡入门"},
            **_face(),
        )
        assert r.status_code == 200, r.text
        assert r.json()["task_id"] == "task-1"
        assert mgr.last_params.get("content_type") == "knowledge"

    def test_digital_still_requires_product_image(self, client):
        c, _ = client
        r = c.post(
            "/digital-human/generate/async",
            data={"mode": "digital"},
            **_face(),  # character only, no product
        )
        assert r.status_code == 400
        assert "product" in r.json()["detail"]

    def test_content_types_endpoint(self, client):
        c, _ = client
        r = c.get("/digital-human/content-types")
        assert r.status_code == 200
        body = r.json()
        assert body["default"] == "knowledge"
        values = [item["value"] for item in body["content_types"]]
        assert values == ["knowledge", "product", "general", "story"]