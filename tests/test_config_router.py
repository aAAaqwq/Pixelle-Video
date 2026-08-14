"""Tests for the /api/config router (Super-AIGC admin linkage).

Covers the masking helpers and the GET/PUT endpoints with a stubbed
config_manager (no config.yaml is required in the test environment).

The test app mounts only the config router so that running the suite does
not pull in the heavy API dependency chain (comfykit / moviepy / etc.).
"""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.config import _is_sensitive_key, _mask_dict, _mask_key, router
from pixelle_video.config import config_manager

app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


def _fake_config(data: dict) -> SimpleNamespace:
    return SimpleNamespace(model_dump=lambda: data)


class TestMaskHelpers:
    def test_sensitive_key_detection(self):
        assert _is_sensitive_key("api_key")
        assert _is_sensitive_key("runninghub_api_key")
        assert _is_sensitive_key("access_key")
        assert _is_sensitive_key("secret_key")
        assert not _is_sensitive_key("base_url")
        assert not _is_sensitive_key("model")

    def test_mask_key_long(self):
        assert _mask_key("sk-abcdefghijkl") == "sk-***ijkl"

    def test_mask_key_short(self):
        assert _mask_key("short") == "configured"

    def test_mask_dict_recursive_and_untouched(self):
        data = {
            "llm": {"api_key": "sk-abcdefghijkl", "base_url": "https://api.deepseek.com"},
            "comfyui": {"runninghub_api_key": "REVOKED-KEY-DO-NOT-USE"},
            "nested": {"deep": {"secret_key": "abc123456789"}},
            "plain": "value",
        }
        masked = _mask_dict(data)
        assert masked["llm"]["api_key"] == "sk-***ijkl"
        assert masked["llm"]["base_url"] == "https://api.deepseek.com"
        assert masked["comfyui"]["runninghub_api_key"] == "0f0***2c83"
        assert masked["nested"]["deep"]["secret_key"] == "abc***6789"
        assert masked["plain"] == "value"
        # Input must stay untouched.
        assert data["llm"]["api_key"] == "sk-abcdefghijkl"


class TestGetConfig:
    def test_masks_sensitive_keys(self, monkeypatch):
        monkeypatch.setattr(
            config_manager,
            "config",
            _fake_config(
                {
                    "llm": {"api_key": "sk-abcdefghijkl", "model": "deepseek-chat"},
                    "comfyui": {"runninghub_api_key": "REVOKED-KEY-DO-NOT-USE"},
                }
            ),
        )
        resp = client.get("/api/config")
        assert resp.status_code == 200
        body = resp.json()
        assert body["llm"]["api_key"] == "sk-***ijkl"
        assert body["comfyui"]["runninghub_api_key"] == "0f0***2c83"


class TestPutConfig:
    def test_valid_update(self, monkeypatch):
        calls: dict = {}
        monkeypatch.setattr(config_manager, "update", lambda body: calls.setdefault("update", body))
        monkeypatch.setattr(config_manager, "save", lambda: calls.setdefault("save", True))
        resp = client.put("/api/config", json={"llm": {"model": "deepseek-chat"}})
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert calls["update"] == {"llm": {"model": "deepseek-chat"}}
        assert calls["save"] is True

    def test_empty_body_rejected(self):
        resp = client.put("/api/config", json={})
        assert resp.status_code == 422

    def test_update_failure_422(self, monkeypatch):
        def boom(_body):
            raise ValueError("bad field")

        monkeypatch.setattr(config_manager, "update", boom)
        resp = client.put("/api/config", json={"llm": {"model": 123}})
        assert resp.status_code == 422
        assert "Configuration update failed" in resp.json()["detail"]
