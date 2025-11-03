# API Overview

Pixelle-Video Python API reference documentation.

---

## Core Classes

### PixelleVideoCore

Main service class providing video generation functionality.

```python
from pixelle_video.service import PixelleVideoCore

pixelle = PixelleVideoCore()
await pixelle.initialize()
```

---

## Main Methods

### generate_video()

Primary method for generating videos.

**Parameters**:

- `text` (str): Topic or complete script
- `mode` (str): Generation mode ("generate" or "fixed")
- `n_scenes` (int): Number of scenes
- `title` (str, optional): Video title
- `tts_workflow` (str): TTS workflow
- `image_workflow` (str): Image generation workflow
- `frame_template` (str): Video template
- `bgm_path` (str, optional): BGM file path

**Returns**: `VideoResult` object

---

## Examples

Check the `examples/` directory for more examples.

---

## More Information

Detailed API documentation coming soon.

