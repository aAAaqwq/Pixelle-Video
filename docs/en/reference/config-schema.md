# Config Schema

Detailed explanation of the `config.yaml` configuration file.

---

## Configuration Structure

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

## LLM Configuration

- `provider`: Provider (currently only supports openai-compatible interfaces)
- `api_key`: API key
- `base_url`: API service address
- `model`: Model name

---

## ComfyUI Configuration

### Basic Configuration

- `comfyui_url`: Local ComfyUI address
- `runninghub_api_key`: RunningHub API key (optional)

### Image Configuration

- `default_workflow`: Default image generation workflow
- `prompt_prefix`: Prompt prefix

### Video Configuration

- `default_workflow`: Default video generation workflow
  - `runninghub/video_wan2.1_fusionx.json`: Cloud workflow (recommended, no local setup required)
  - `selfhost/video_wan2.1_fusionx.json`: Local workflow (requires local ComfyUI support)
- `prompt_prefix`: Video prompt prefix (controls video generation style)

### TTS Configuration

- `default_workflow`: Default TTS workflow

---

## More Information

The configuration file is automatically created on first run.

