# Pixelle-Video Capabilities Guide

> Complete guide to using LLM, TTS, and Image generation capabilities

## Overview

Pixelle-Video provides three core AI capabilities:
- **LLM**: Text generation using LiteLLM (supports 100+ models)
- **TTS**: Text-to-speech using Edge TTS (free, 400+ voices)
- **Image**: Image generation using ComfyKit (local or cloud)

## Quick Start

```python
from pixelle_video.service import pixelle_video

# LLM - Generate text
answer = await pixelle_video.llm("Summarize 'Atomic Habits' in 3 sentences")

# TTS - Generate speech
audio_path = await pixelle_video.tts("Hello, world!")

# Image - Generate images
image_url = await pixelle_video.image(
    workflow="workflows/book_cover_simple.json",
    prompt="minimalist book cover design"
)
```

---

## 1. LLM (Large Language Model)

### Configuration

Edit `config.yaml`:

```yaml
llm:
  default: qwen  # Choose: qwen, openai, deepseek, ollama
  
  qwen:
    api_key: "your-dashscope-api-key"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: "openai/qwen-max"
  
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
  
  deepseek:
    api_key: "your-deepseek-api-key"
    base_url: "https://api.deepseek.com"
    model: "openai/deepseek-chat"
  
  ollama:
    base_url: "http://localhost:11434"
    model: "ollama/llama3.2"
```

### Usage

```python
# Basic usage
answer = await pixelle_video.llm("What is machine learning?")

# With parameters
answer = await pixelle_video.llm(
    prompt="Explain atomic habits",
    temperature=0.7,  # 0.0-2.0 (lower = more deterministic)
    max_tokens=2000
)
```

### Environment Variables (Alternative)

Instead of `config.yaml`, you can use environment variables:

```bash
# Qwen
export DASHSCOPE_API_KEY="your-key"

# OpenAI
export OPENAI_API_KEY="your-key"

# DeepSeek
export DEEPSEEK_API_KEY="your-key"
```

---

## 2. TTS (Text-to-Speech)

### Configuration

Edit `config.yaml`:

```yaml
tts:
  default: edge
  
  edge:
    # No configuration needed - free to use!
```

### Usage

```python
# Basic usage (auto-generates temp path)
audio_path = await pixelle_video.tts("Hello, world!")
# Returns: "temp/abc123def456.mp3"

# With Chinese text
audio_path = await pixelle_video.tts(
    text="你好，世界！",
    voice="zh-CN-YunjianNeural"
)

# With custom parameters
audio_path = await pixelle_video.tts(
    text="Welcome to Pixelle-Video",
    voice="en-US-JennyNeural",
    rate="+20%",  # Speed: +50% = faster, -20% = slower
    volume="+0%",
    pitch="+0Hz"
)

# Specify output path
audio_path = await pixelle_video.tts(
    text="Hello",
    output_path="output/greeting.mp3"
)
```

### Popular Voices

**Chinese:**
- `zh-CN-YunjianNeural` (male, default)
- `zh-CN-XiaoxiaoNeural` (female)
- `zh-CN-YunxiNeural` (male)
- `zh-CN-XiaoyiNeural` (female)

**English:**
- `en-US-JennyNeural` (female)
- `en-US-GuyNeural` (male)
- `en-GB-SoniaNeural` (female, British)

### List All Voices

```python
# Get all available voices
voices = await pixelle_video.tts.list_voices()

# Get Chinese voices only
voices = await pixelle_video.tts.list_voices(locale="zh-CN")

# Get English voices only
voices = await pixelle_video.tts.list_voices(locale="en-US")
```

---

## 3. Image Generation

### Configuration

Edit `config.yaml`:

```yaml
image:
  default: comfykit
  
  comfykit:
    # Local ComfyUI (optional, default: http://127.0.0.1:8188)
    comfyui_url: "http://127.0.0.1:8188"
    
    # RunningHub cloud (optional)
    runninghub_api_key: "rh-key-xxx"
```

### Usage

```python
# Basic usage (local ComfyUI)
image_url = await pixelle_video.image(
    workflow="workflows/book_cover_simple.json",
    prompt="minimalist book cover design, blue and white"
)

# With full parameters
image_url = await pixelle_video.image(
    workflow="workflows/book_cover_simple.json",
    prompt="book cover for 'Atomic Habits', professional, minimalist",
    negative_prompt="ugly, blurry, low quality",
    width=1024,
    height=1536,
    steps=20,
    seed=42
)

# Using RunningHub cloud
image_url = await pixelle_video.image(
    workflow="12345",  # RunningHub workflow ID
    prompt="a beautiful landscape"
)

# Check available workflows
workflows = pixelle_video.image.list_workflows()
print(f"Available workflows: {workflows}")
```

### Environment Variables (Alternative)

```bash
# Local ComfyUI
export COMFYUI_BASE_URL="http://127.0.0.1:8188"

# RunningHub cloud
export RUNNINGHUB_API_KEY="rh-key-xxx"
```

### Workflow DSL

Pixelle-Video uses ComfyKit's DSL for workflow parameters:

```json
{
  "6": {
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "$prompt!"
    },
    "inputs": {
      "text": "default prompt",
      "clip": ["4", 1]
    }
  }
}
```

**DSL Markers:**
- `$param!` - Required parameter
- `$param` - Optional parameter
- `$param~` - Upload parameter (for images/audio/video)
- `$output.name` - Output variable

---

## Combined Workflow Example

Generate a complete book cover with narration:

```python
import asyncio
from pixelle_video.service import pixelle_video

async def create_book_content(book_title, author):
    """Generate book summary, audio, and cover image"""
    
    # 1. Generate book summary with LLM
    summary = await pixelle_video.llm(
        prompt=f"Write a compelling 2-sentence summary for a book titled '{book_title}' by {author}",
        max_tokens=100
    )
    print(f"Summary: {summary}")
    
    # 2. Generate audio narration with TTS
    audio_path = await pixelle_video.tts(
        text=summary,
        voice="en-US-JennyNeural"
    )
    print(f"Audio: {audio_path}")
    
    # 3. Generate book cover image
    image_url = await pixelle_video.image(
        workflow="workflows/book_cover_simple.json",
        prompt=f"book cover for '{book_title}' by {author}, professional, modern design",
        width=1024,
        height=1536
    )
    print(f"Cover: {image_url}")
    
    return {
        "summary": summary,
        "audio": audio_path,
        "cover": image_url
    }

# Run
result = asyncio.run(create_book_content("Atomic Habits", "James Clear"))
```

---

## Troubleshooting

### LLM Issues

**"API key not found"**
- Make sure you've set the API key in `config.yaml` or environment variables
- For Qwen: `DASHSCOPE_API_KEY`
- For OpenAI: `OPENAI_API_KEY`
- For DeepSeek: `DEEPSEEK_API_KEY`

**"Connection error"**
- Check `base_url` in config
- Verify API endpoint is accessible
- For Ollama, make sure server is running (`ollama serve`)

### TTS Issues

**"SSL error"**
- Edge TTS is free but requires internet connection
- SSL verification is disabled by default for development

### Image Issues

**"ComfyUI connection refused"**
- Make sure ComfyUI is running at http://127.0.0.1:8188
- Or configure RunningHub API key for cloud execution

**"Workflow file not found"**
- Check workflow path is correct
- Use relative path from project root: `workflows/your_workflow.json`

**"No images generated"**
- Check workflow has `SaveImage` node
- Verify workflow parameters are correct
- Check ComfyUI logs for errors

---

## Next Steps

- See `/examples/` directory for complete examples
- Run `python test_integration.py` to test all capabilities
- Create custom workflows in `/workflows/` directory
- Check ComfyKit documentation: https://puke3615.github.io/ComfyKit

---

**Happy creating with Pixelle-Video!** 📚🎬

