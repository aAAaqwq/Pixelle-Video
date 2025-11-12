# 配置文件详解

`config.yaml` 配置文件的详细说明。

---

## 配置结构

```yaml
llm:
  provider: openai
  api_key: "your-api-key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-plus"

comfyui:
  comfyui_url: "http://127.0.0.1:8188"
  runninghub_api_key: ""
  
  image:
    default_workflow: "runninghub/image_flux.json"
    prompt_prefix: "Minimalist illustration style"
  
  video:
    default_workflow: "runninghub/video_wan2.1_fusionx.json"
    prompt_prefix: "Minimalist illustration style"
  
  tts:
    default_workflow: "selfhost/tts_edge.json"
```

---

## LLM 配置

- `provider`: 提供商（目前仅支持 openai 兼容接口）
- `api_key`: API 密钥
- `base_url`: API 服务地址
- `model`: 模型名称

---

## ComfyUI 配置

### 基础配置

- `comfyui_url`: 本地 ComfyUI 地址
- `runninghub_api_key`: RunningHub API 密钥（可选）

### 图像配置

- `default_workflow`: 默认图像生成工作流
- `prompt_prefix`: 提示词前缀

### 视频配置

- `default_workflow`: 默认视频生成工作流
  - `runninghub/video_wan2.1_fusionx.json`: 云端工作流（推荐，无需本地环境）
  - `selfhost/video_wan2.1_fusionx.json`: 本地工作流（需要本地 ComfyUI 支持）
- `prompt_prefix`: 视频提示词前缀（用于控制视频生成风格）

### TTS 配置

- `default_workflow`: 默认 TTS 工作流

---

## 更多信息

配置文件会自动在首次运行时创建。

