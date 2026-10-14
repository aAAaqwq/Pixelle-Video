"""Regression tests: a missing OPTIONAL workflow output must not fail the run.

mode="digital" reads two things off the digital_image workflow result — the promo
frame and the script the workflow wrote alongside it. Both are optional: the script
is only a fallback for an empty goods_text (content_type generates one otherwise),
and the frame has its own explicit "Failed to obtain a talking-head image" error.

``getattr(result, name, [None])[0]`` guards the wrong case — a getattr default only
applies when the attribute is ABSENT — so an empty list from ComfyKit reached the
subscript and raised IndexError. In production that turned a transient download miss
on RunningHub's ``.txt`` script output into a hard failure of every mode="digital"
run, surfacing to callers as the meaningless "list index out of range".

No network / RunningHub / TTS: the core, the ComfyKit kit, the workflow loader and
the final download are all replaced.
"""

from __future__ import annotations

import types

import pytest

from pixelle_video.pipelines import digital_human_service as dh


class _Result:
    """Stands in for a ComfyKit ExecuteResult."""

    def __init__(self, *, status: str = "completed", images=(), texts=(), videos=()):
        self.status = status
        self.images = list(images)
        self.texts = list(texts)
        self.videos = list(videos)


class _FakeKit:
    """Returns one canned result per execute() call, in order."""

    def __init__(self, *results: _Result):
        self._results = list(results)
        self.calls: list[tuple[str, dict]] = []

    async def execute(self, workflow: str, params: dict) -> _Result:
        self.calls.append((workflow, params))
        return self._results.pop(0)


class _FakeCore:
    """Stands in for PixelleVideoCore: canned kit, script LLM and TTS."""

    def __init__(self, kit: _FakeKit, narration: str = "由 content_type 生成的文案"):
        self._kit = kit
        self._narration = narration
        self.tts_calls: list[dict] = []
        self.config = {"llm": {"model": "gpt-4o", "base_url": "https://api.openai.com/v1"}}

    async def _get_or_create_comfykit(self) -> _FakeKit:
        return self._kit

    async def llm(self, **kwargs) -> str:
        return self._narration

    async def tts(self, **kwargs) -> None:
        self.tts_calls.append(kwargs)


class _FakeResponse:
    content = b"fake-video-bytes"

    def raise_for_status(self) -> None:
        pass


class _FakeAsyncClient:
    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc) -> bool:
        return False

    async def get(self, url: str) -> _FakeResponse:
        return _FakeResponse()


@pytest.fixture
def wired(monkeypatch, tmp_path):
    """Point the module's external edges (workflow file, output dir, download) at fakes."""

    def _wire(kit: _FakeKit) -> _FakeCore:
        core = _FakeCore(kit)
        monkeypatch.setattr(dh, "_load_workflow_input", lambda path: "stub-workflow-id")
        monkeypatch.setattr(
            dh, "create_task_output_dir", lambda task_id=None: (str(tmp_path), "task-1")
        )
        monkeypatch.setattr(
            dh,
            "httpx",
            types.SimpleNamespace(AsyncClient=_FakeAsyncClient, Timeout=lambda *a, **k: None),
        )
        return core

    return _wire


# --------------------------------------------------------------------------- #
# _first_output — the accessor the two call sites were rewritten onto
# --------------------------------------------------------------------------- #


class TestFirstOutput:
    def test_empty_list_is_none_not_index_error(self):
        assert dh._first_output(_Result(texts=[]), "texts") is None

    def test_missing_attribute_is_none(self):
        assert dh._first_output(object(), "texts") is None

    def test_absent_list_is_none(self):
        result = _Result()
        result.texts = None
        assert dh._first_output(result, "texts") is None

    def test_returns_first_value(self):
        assert dh._first_output(_Result(texts=["a", "b"]), "texts") == "a"


# --------------------------------------------------------------------------- #
# mode="digital" end to end, with and without each optional output
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
class TestDigitalModeOptionalOutputs:
    async def _run(self, image_result: _Result, wired, **kwargs):
        core = wired(_FakeKit(image_result, _Result(videos=["https://example.test/out.mp4"])))
        return await dh.generate_digital_human(
            core,
            mode="digital",
            character_image="/tmp/face.png",
            product_image="/tmp/product.png",
            goods_title="商品",
            **kwargs,
        )

    async def test_missing_script_output_still_completes(self, wired):
        # The production failure: workflow returned the frame but the .txt script
        # download failed, so texts was empty. Used to raise IndexError.
        out = await self._run(_Result(images=["https://example.test/frame.png"], texts=[]), wired)
        assert out["image_url"] == "https://example.test/frame.png"
        assert out["script"] == "由 content_type 生成的文案"

    async def test_workflow_script_is_used_when_no_goods_text(self, wired):
        out = await self._run(
            _Result(images=["https://example.test/frame.png"], texts=["工作流写的文案"]), wired
        )
        assert out["script"] == "工作流写的文案"

    async def test_explicit_goods_text_still_wins(self, wired):
        out = await self._run(
            _Result(images=["https://example.test/frame.png"], texts=["工作流写的文案"]),
            wired,
            goods_text="用户写的文案",
        )
        assert out["script"] == "用户写的文案"

    async def test_missing_image_output_raises_a_readable_error(self, wired):
        # An empty images list must surface as the module's own error, not IndexError.
        with pytest.raises(RuntimeError, match="talking-head image"):
            await self._run(_Result(images=[], texts=[]), wired)
