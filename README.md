# ReelForge 🔨

> **Forge Your Perfect Reel Engine**
> 
> The modular video creation platform where every creator forges differently.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [简体中文](README_CN.md)

---

## 🔥 What is ReelForge?

ReelForge is not just another video generation tool.

**It's a forge** - where you choose your materials (LLM, TTS, image generators), 
heat them in your fire (configuration), and hammer them into your perfect 
video creation engine.

### vs Traditional Tools

```
Traditional Tools        ReelForge
━━━━━━━━━━━━━━━        ━━━━━━━━━━━━
Fixed workflow      →   Modular & Customizable
One-size-fits-all   →   Forge Your Own
Closed system       →   Open & Extensible
```

---

## ⚒️ Core Philosophy

**Every creator forges differently.**

- 🎯 **Modular by Design** - Swap TTS, image gen, frame templates
- 🔧 **Plug & Play** - Use built-in or bring your own
- 🎨 **DIY Workflows** - Customize every step of generation
- 🌐 **Open Source** - Community-driven and transparent

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ReelForge.git
cd ReelForge

# Install dependencies with uv
uv sync

# Copy config example
cp config.example.yaml config.yaml

# Edit config.yaml and fill in your API keys
```

### Your First Forge

```bash
# Run the web interface
uv run python web.py

# Or use CLI
uv run reelforge --help
```

### Programmatic Usage

```python
from reelforge.service import reelforge

# Initialize
await reelforge.initialize()

# Generate a video
result = await reelforge.book_video_workflow.generate(
    book_name="Atomic Habits",
    n_storyboard=5
)

print(f"Forged: {result.video_path}")
```

---

## 🔨 What Makes ReelForge Different?

### 1. **Truly Modular Architecture**

Swap components like changing tools in your forge:

```yaml
# config.yaml
llm:
  api_key: your_key
  model: qwen-max

tts:
  default: edge  # or azure, elevenlabs

image:
  default: comfykit
  comfykit:
    comfyui_url: http://localhost:8188
```

### 2. **Capability-Based System**

Every capability follows a simple naming convention:

```
{type}_{id}

Examples:
  llm_qwen         → LLM capability, ID: qwen
  tts_edge         → TTS capability, ID: edge
  image_comfykit   → Image capability, ID: comfykit
```

### 3. **Storyboard-Based Generation**

Unlike simple template filling, ReelForge uses AI to:
- Understand your topic deeply
- Generate narrative storyboards
- Create scene-by-scene visuals
- Compose professional videos

---

## 🏗️ Architecture

```
ReelForge Core
├── Capabilities (Pluggable)
│   ├── LLM (OpenAI, Qwen, Ollama, ...)
│   ├── TTS (Edge, Azure, ElevenLabs, ...)
│   ├── Image (ComfyUI, SD, DALL-E, ...)
│   └── Custom (Your own!)
├── Services (Composable)
│   ├── Narration Generator
│   ├── Image Prompt Generator
│   ├── Storyboard Processor
│   ├── Frame Composer
│   └── Video Compositor
└── Workflows (Customizable)
    └── Define your own pipeline
```

---

## 🎨 Built-in Capabilities

### LLM (Large Language Models)

| Provider | ID | API Key Required |
|----------|----|----|
| 通义千问 | `qwen` | ✅ DASHSCOPE_API_KEY |
| OpenAI GPT | `openai` | ✅ OPENAI_API_KEY |
| DeepSeek | `deepseek` | ✅ DEEPSEEK_API_KEY |
| Ollama | `ollama` | ❌ No (runs locally) |

### TTS (Text-to-Speech)

| Provider | ID | Features |
|----------|----|----|
| Edge TTS | `edge` | Free, Multiple voices |
| Azure TTS | `azure` | Premium quality |

### Image Generation

| Provider | ID | Features |
|----------|----|----|
| ComfyKit | `comfykit` | Custom workflows, Local |
| (More coming) | - | - |

---

## 📚 Examples

Check out the `examples/` directory:

- `generate_video_simple.py` - Basic video generation
- `generate_video_with_bgm.py` - Add background music
- `generate_video_with_image_style.py` - Custom image styles
- `generate_video_custom.py` - Full customization

---

## 🤝 Contributing

ReelForge is **community-driven**.

- 🐛 [Report bugs](https://github.com/YOUR_USERNAME/ReelForge/issues)
- 💡 [Request features](https://github.com/YOUR_USERNAME/ReelForge/discussions)
- 🔧 [Build components](CONTRIBUTING.md)
- 🎨 Share your forge configurations

---

## 🗺️ Roadmap

- [x] Core modular architecture
- [x] Built-in LLM/TTS/Image capabilities
- [x] Storyboard-based generation
- [x] Web interface (Streamlit)
- [ ] Visual forge builder
- [ ] Community forge marketplace
- [ ] Plugin ecosystem
- [ ] Cloud hosting

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with ❤️ by the creator community.

Inspired by:
- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)
- [NarratoAI](https://github.com/linyqh/NarratoAI)

---

<p align="center">
  <strong>Forge Your Way</strong>
  <br>
  Every creator forges differently. What will you forge?
</p>

---

**Star us if you like what we're building!** ⭐
