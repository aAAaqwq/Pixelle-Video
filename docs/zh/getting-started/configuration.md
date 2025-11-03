# 配置说明

完成安装后，需要配置服务才能使用 Pixelle-Video。

---

## LLM 配置

LLM（大语言模型）用于生成视频文案。

### 快速选择预设

1. 从下拉菜单选择预设模型：
   - 通义千问（推荐，性价比高）
   - GPT-4o
   - DeepSeek
   - Ollama（本地运行，完全免费）

2. 系统会自动填充 `base_url` 和 `model`

3. 点击「🔑 获取 API Key」链接，注册并获取密钥

4. 填入 API Key

---

## 图像配置

支持两种方式：

### 本地部署（推荐）

使用本地 ComfyUI 服务：

1. 安装并启动 ComfyUI
2. 填写 ComfyUI URL（默认 `http://127.0.0.1:8188`）
3. 点击「测试连接」确认服务可用

### 云端部署

使用 RunningHub 云端服务：

1. 注册 RunningHub 账号
2. 获取 API Key
3. 在配置中填写 API Key

---

## 保存配置

填写完所有必需的配置后，点击「保存配置」按钮。

配置会保存到 `config.yaml` 文件中。

---

## 下一步

- [快速开始](quick-start.md) - 生成你的第一个视频

