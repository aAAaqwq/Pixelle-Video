# API 概览

Pixelle-Video Python API 参考文档。

---

## 核心类

### PixelleVideoCore

主要服务类，提供视频生成功能。

```python
from pixelle_video.service import PixelleVideoCore

pixelle = PixelleVideoCore()
await pixelle.initialize()
```

---

## 主要方法

### generate_video()

生成视频的主要方法。

**参数**:

- `text` (str): 主题或完整文案
- `mode` (str): 生成模式 ("generate" 或 "fixed")
- `n_scenes` (int): 分镜数量
- `title` (str, optional): 视频标题
- `tts_workflow` (str): TTS 工作流
- `image_workflow` (str): 图像生成工作流
- `frame_template` (str): 视频模板
- `bgm_path` (str, optional): BGM 文件路径

**返回**: `VideoResult` 对象

---

## 示例

查看 `examples/` 目录获取更多示例。

---

## 更多信息

详细的 API 文档即将推出。

