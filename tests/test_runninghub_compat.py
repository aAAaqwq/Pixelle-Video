import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class RunningHubCompatTests(unittest.IsolatedAsyncioTestCase):
    async def test_v2_upload_uses_cn_endpoint_and_returns_filename(self):
        from pixelle_video.services.runninghub_compat import RunningHubV2Client

        with tempfile.TemporaryDirectory() as temp_dir:
            media = Path(temp_dir) / "avatar.png"
            media.write_bytes(b"fake-png")

            class RecordingClient(RunningHubV2Client):
                def __init__(self):
                    super().__init__(api_key="test-key")
                    self.calls = []

                async def _upload_once(self, file_path: Path):
                    self.calls.append((self.base_url, self.upload_endpoint, file_path))
                    return {"code": 0, "data": {"fileName": "openapi/avatar.png"}}

            client = RecordingClient()
            self.assertEqual(await client.upload_file(str(media)), "openapi/avatar.png")
            self.assertEqual(
                client.calls,
                [("https://www.runninghub.cn", "/openapi/v2/media/upload/binary", media)],
            )

    async def test_v2_upload_rejects_missing_filename(self):
        from pixelle_video.services.runninghub_compat import RunningHubV2Client

        with tempfile.TemporaryDirectory() as temp_dir:
            media = Path(temp_dir) / "avatar.png"
            media.write_bytes(b"fake-png")

            class MissingFilenameClient(RunningHubV2Client):
                async def _upload_once(self, file_path: Path):
                    return {"code": 0, "data": {}}

            client = MissingFilenameClient(api_key="test-key")
            with self.assertRaisesRegex(RuntimeError, "fileName"):
                await client.upload_file(str(media))

    def test_install_replaces_comfykit_runninghub_client(self):
        import comfykit.comfyui.runninghub_executor as executor_module
        from pixelle_video.services.runninghub_compat import (
            RunningHubV2Client,
            install_runninghub_v2_compat,
        )

        with patch.object(executor_module, "RunningHubClient", object):
            install_runninghub_v2_compat()
            self.assertIs(executor_module.RunningHubClient, RunningHubV2Client)

    def test_redact_comfykit_config_masks_api_keys(self):
        from pixelle_video.services.runninghub_compat import redact_comfykit_config

        config = {
            "runninghub_api_key": "example",
            "api_key": "x",
            "comfyui_url": "http://127.0.0.1:8188",
        }

        self.assertEqual(
            redact_comfykit_config(config),
            {
                "runninghub_api_key": "***xample",
                "api_key": "***",
                "comfyui_url": "http://127.0.0.1:8188",
            },
        )


if __name__ == "__main__":
    unittest.main()
