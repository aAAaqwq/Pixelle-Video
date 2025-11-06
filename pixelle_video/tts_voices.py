"""
TTS Voice Configuration

Defines available voices for local Edge TTS inference.
"""

from typing import List, Dict, Any


# Edge TTS voice presets for local inference
EDGE_TTS_VOICES: List[Dict[str, Any]] = [
    # Chinese voices
    {
        "id": "zh-CN-XiaoxiaoNeural",
        "label_key": "tts.voice.zh_CN_XiaoxiaoNeural",
        "locale": "zh-CN",
        "gender": "female"
    },
    {
        "id": "zh-CN-XiaoyiNeural",
        "label_key": "tts.voice.zh_CN_XiaoyiNeural",
        "locale": "zh-CN",
        "gender": "female"
    },
    {
        "id": "zh-CN-YunjianNeural",
        "label_key": "tts.voice.zh_CN_YunjianNeural",
        "locale": "zh-CN",
        "gender": "male"
    },
    {
        "id": "zh-CN-YunxiNeural",
        "label_key": "tts.voice.zh_CN_YunxiNeural",
        "locale": "zh-CN",
        "gender": "male"
    },
    {
        "id": "zh-CN-YunyangNeural",
        "label_key": "tts.voice.zh_CN_YunyangNeural",
        "locale": "zh-CN",
        "gender": "male"
    },
    {
        "id": "zh-CN-YunyeNeural",
        "label_key": "tts.voice.zh_CN_YunyeNeural",
        "locale": "zh-CN",
        "gender": "male"
    },
    {
        "id": "zh-CN-YunfengNeural",
        "label_key": "tts.voice.zh_CN_YunfengNeural",
        "locale": "zh-CN",
        "gender": "male"
    },
    {
        "id": "zh-CN-liaoning-XiaobeiNeural",
        "label_key": "tts.voice.zh_CN_liaoning_XiaobeiNeural",
        "locale": "zh-CN",
        "gender": "female"
    },
    
    # English voices
    {
        "id": "en-US-AriaNeural",
        "label_key": "tts.voice.en_US_AriaNeural",
        "locale": "en-US",
        "gender": "female"
    },
    {
        "id": "en-US-JennyNeural",
        "label_key": "tts.voice.en_US_JennyNeural",
        "locale": "en-US",
        "gender": "female"
    },
    {
        "id": "en-US-GuyNeural",
        "label_key": "tts.voice.en_US_GuyNeural",
        "locale": "en-US",
        "gender": "male"
    },
    {
        "id": "en-US-DavisNeural",
        "label_key": "tts.voice.en_US_DavisNeural",
        "locale": "en-US",
        "gender": "male"
    },
    {
        "id": "en-GB-SoniaNeural",
        "label_key": "tts.voice.en_GB_SoniaNeural",
        "locale": "en-GB",
        "gender": "female"
    },
    {
        "id": "en-GB-RyanNeural",
        "label_key": "tts.voice.en_GB_RyanNeural",
        "locale": "en-GB",
        "gender": "male"
    },
]


def get_voice_display_name(voice_id: str, tr_func=None, locale: str = "zh_CN") -> str:
    """
    Get display name for voice
    
    Args:
        voice_id: Voice ID (e.g., "zh-CN-YunjianNeural")
        tr_func: Translation function (optional)
        locale: Current locale (default: "zh_CN")
    
    Returns:
        Display name (translated label if in Chinese, otherwise voice ID)
    """
    # Find voice config
    voice_config = next((v for v in EDGE_TTS_VOICES if v["id"] == voice_id), None)
    
    if not voice_config:
        return voice_id
    
    # If Chinese locale and translation function available, use translated label
    if locale == "zh_CN" and tr_func:
        label_key = voice_config["label_key"]
        return tr_func(label_key)
    
    # For other locales, return voice ID
    return voice_id


def speed_to_rate(speed: float) -> str:
    """
    Convert speed multiplier to Edge TTS rate parameter
    
    Args:
        speed: Speed multiplier (1.0 = normal, 1.2 = 120%)
    
    Returns:
        Rate string (e.g., "+20%", "-10%")
    
    Examples:
        1.0 → "+0%"
        1.2 → "+20%"
        0.8 → "-20%"
    """
    percentage = int((speed - 1.0) * 100)
    sign = "+" if percentage >= 0 else ""
    return f"{sign}{percentage}%"

