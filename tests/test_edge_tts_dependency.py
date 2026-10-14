"""Offline regression checks for the Edge speech service's v2 protocol."""

import re
import tomllib
from pathlib import Path

from edge_tts.constants import SEC_MS_GEC_VERSION
from edge_tts.drm import DRM

ROOT = Path(__file__).resolve().parents[1]


def test_edge_tts_pin_and_lock_use_v2_compatible_release():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    assert "edge-tts==7.3.1" in project["project"]["dependencies"]
    package = next(p for p in lock["package"] if p["name"] == "edge-tts")
    assert package["version"] == "7.3.1"


def test_installed_edge_tts_sends_v2_version_and_token():
    # Microsoft's endpoint rejects the legacy v1 handshake with HTTP 403.
    assert SEC_MS_GEC_VERSION.startswith("2-")
    assert re.fullmatch(r"[0-9A-F]{16}-[0-9A-F]{64}", DRM.generate_sec_ms_gec())
