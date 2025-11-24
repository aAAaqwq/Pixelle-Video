# 🙋‍♀️ Pixelle-Video Frequently Asked Questions

### What is Pixelle-Video and how does it work?

Pixelle-Video is an AI-powered video generation tool that creates complete videos from a single topic input. The workflow is:
- **Script Generation** → **Image Planning** → **Frame Processing** → **Video Synthesis**

Simply input a topic keyword, and Pixelle-Video automatically handles scriptwriting, image generation, voice synthesis, background music, and final video compilation - requiring zero video editing experience.

### What installation methods are supported?

Pixelle-Video supports the following installation methods:

1. **Standard Installation**:
   ```bash
   git clone https://github.com/AIDC-AI/Pixelle-Video.git
   cd Pixelle-Video
   uv run streamlit run web/app.py
   ```

2. **Prerequisites**:
   - Install `uv` package manager (see official documentation for your system)
   - Install `ffmpeg` for video processing:
     - **macOS**: `brew install ffmpeg`
     - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
     - **Windows**: Download from ffmpeg.org and add to PATH

### What are the system requirements?

- **Basic**: Python 3.10+, uv package manager, ffmpeg
- **For Image Generation**: ComfyUI server (local or cloud)
- **For LLM Integration**: API keys for supported models (optional for local models)
- **Hardware**: GPU recommended for local image generation, but cloud options available

### How to configure the system for first use?

1. Open the web interface at http://localhost:8501
2. Expand the "⚙️ System Configuration" panel
3. Configure two main sections:
   - **LLM Configuration**: 
     - Select preset model (Qwen, GPT-4o, DeepSeek, etc.)
     - Enter API key or configure local model (Ollama)
   - **Image Configuration**:
     - **Local deployment**: Set ComfyUI URL (default: http://127.0.0.1:8188)
     - **Cloud deployment**: Enter RunningHub API key
4. Click "Save Configuration" to complete setup

### What generation modes are available?

Pixelle-Video offers two main generation modes:

1. **AI Generated Content**:
   - Input just a topic keyword
   - AI automatically writes the script and creates the video
   - Example: "Why develop a reading habit"

2. **Fixed Script Content**:
   - Provide your complete script text
   - Skip AI scriptwriting, go directly to video generation
   - Ideal when you already have prepared content

### How to customize the audio settings?

Audio customization options include:

- **Background Music (BGM)**:
  - No BGM: Pure voice narration
  - Built-in music: Select from preset tracks (e.g., default.mp3)
  - Custom music: Place your MP3/WAV files in the `bgm/` folder

- **Text-to-Speech (TTS)**:
  - Select from available TTS workflows (Edge-TTS, Index-TTS, etc.)
  - System automatically scans `workflows/` folder for available options
  - Preview voice effect with test text

- **Voice Cloning**:
  - Upload reference audio (MP3/WAV/FLAC) for supported TTS workflows
  - Use reference audio during preview and generation

### How to customize the visual style?

Visual customization includes:

- **Image Generation Workflow**:
  - Select from available ComfyUI workflows (local or cloud)
  - Default workflow: `image_flux.json`
  - Custom workflows can be added to `workflows/` folder

- **Image Dimensions**:
  - Set width and height in pixels (default: 1024x1024)
  - Note: Different models have different size limitations

- **Style Prompt Prefix**:
  - Control overall image style (must be in English)
  - Example: "Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style"
  - Click "Preview Style" to test the effect

- **Video Templates**:
  - Choose from multiple templates grouped by aspect ratio (vertical/horizontal/square)
  - Preview templates with custom parameters
  - Advanced users can create custom HTML templates in `templates/` folder

### What AI models are supported?

Pixelle-Video supports multiple AI model providers:

- **LLM Models**: GPT, Qwen (通义千问), DeepSeek, Ollama (local)
- **Image Generation**: ComfyUI with various models (FLUX, SDXL, etc.)
- **TTS Engines**: Edge-TTS, Index-TTS, ChatTTS, and more

The modular architecture allows flexible replacement of any component - for example, you can replace the image generation model with FLUX or switch TTS to ChatTTS.

### What are the cost options for running Pixelle-Video?

Pixelle-Video offers three cost tiers:

1. **Completely Free**:
   - LLM: Ollama (local)
   - Image Generation: Local ComfyUI deployment
   - Total cost: $0

2. **Recommended Balanced Option**:
   - LLM: Qwen (通义千问) - very low cost, high value
   - Image Generation: Local ComfyUI deployment
   - Cost: Minimal API fees for text generation only

3. **Cloud-Only Option**:
   - LLM: OpenAI API
   - Image Generation: RunningHub cloud service
   - Cost: Higher but requires no local hardware

**Recommendation**: Use local deployment if you have a GPU, otherwise Qwen + local ComfyUI offers the best value.

### How long does video generation take?

Generation time depends on several factors:
- Number of scenes in the script
- Network speed for API calls
- AI inference speed (local vs cloud)
- Video length and resolution

Typical generation time: **2-10 minutes** for most videos. The interface shows real-time progress through each stage (script → images → audio → final video).

### What to do if the video quality is unsatisfactory?

Try these adjustments:

- **Script Quality**:
  - Switch to a different LLM model (different models have different writing styles)
  - Use "Fixed Script Content" mode with your own refined script

- **Image Quality**:
  - Adjust image dimensions to match model requirements
  - Modify the prompt prefix to change visual style
  - Try different ComfyUI workflows

- **Audio Quality**:
  - Switch TTS workflow (Edge-TTS vs Index-TTS vs others)
  - Upload reference audio for voice cloning
  - Adjust TTS parameters

- **Video Layout**:
  - Try different video templates
  - Change video dimensions (vertical/horizontal/square)

### Where are the generated videos saved?

All generated videos are automatically saved to the `output/` folder in the project directory. The interface displays detailed information after generation:
- Video duration
- File size
- Number of scenes
- Download link

### How to troubleshoot common errors?

1. **FFmpeg Errors**:
   - Verify ffmpeg installation with `ffmpeg -version`
   - Ensure ffmpeg is in your system PATH

2. **API Connection Issues**:
   - Verify API keys are correct
   - Test LLM connection in system configuration
   - For ComfyUI: Click "Test Connection" in image configuration

3. **Image Generation Failures**:
   - Ensure ComfyUI server is running
   - Check image dimensions are supported by your model
   - Verify workflow files exist in `workflows/` folder

4. **Audio Generation Issues**:
   - Ensure selected TTS workflow is properly configured
   - For voice cloning: verify reference audio format is supported

### How to extend Pixelle-Video with custom features?

Pixelle-Video is built on ComfyUI architecture, allowing deep customization:

- **Custom Workflows**: Add your own ComfyUI workflows to `workflows/` folder
- **Custom Templates**: Create HTML templates in `templates/` folder
- **Custom BGM**: Add your music files to `bgm/` folder
- **Advanced Integration**: Since it's based on ComfyUI, you can integrate any ComfyUI custom nodes

The atomic capability design means you can mix and match any component - replace text generation, image models, TTS engines, or video templates independently.

### What community resources are available?

- **GitHub Repository**: https://github.com/AIDC-AI/Pixelle-Video
- **Issue Tracking**: Submit bugs or feature requests via GitHub Issues
- **Community Support**: Join discussion groups for help and sharing
- **Template Gallery**: View all available templates and their effects
- **Contributions**: The project welcomes contributions under MIT license

💡 **Tip**: If your question isn't answered here, please submit an issue on GitHub or join our community discussions. We continuously update this FAQ based on user feedback!
