"""
International language support for ReelForge
"""

import json
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

_locales: Dict[str, dict] = {}
_current_language: str = "zh_CN"


def load_locales() -> Dict[str, dict]:
    """Load all locale files from locales directory"""
    global _locales
    
    locales_dir = Path(__file__).parent / "locales"
    
    if not locales_dir.exists():
        logger.warning(f"Locales directory not found: {locales_dir}")
        return _locales
    
    for json_file in locales_dir.glob("*.json"):
        lang_code = json_file.stem
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                _locales[lang_code] = json.load(f)
            logger.debug(f"Loaded locale: {lang_code}")
        except Exception as e:
            logger.error(f"Failed to load locale {lang_code}: {e}")
    
    logger.info(f"Loaded {len(_locales)} locales: {list(_locales.keys())}")
    return _locales


def set_language(lang_code: str):
    """Set current language"""
    global _current_language
    if lang_code in _locales:
        _current_language = lang_code
        logger.debug(f"Language set to: {lang_code}")
    else:
        logger.warning(f"Language {lang_code} not found, keeping {_current_language}")


def get_language() -> str:
    """Get current language"""
    return _current_language


def tr(key: str, fallback: Optional[str] = None, **kwargs) -> str:
    """
    Translate a key to current language
    
    Args:
        key: Translation key (e.g., "app.title")
        fallback: Fallback text if key not found
        **kwargs: Format parameters for string interpolation
    
    Returns:
        Translated text
    
    Example:
        tr("app.title")  # => "ReelForge - AI书单视频生成器"
        tr("error.missing_field", field="API Key")  # => "请填写 API Key"
    """
    locale = _locales.get(_current_language, {})
    translations = locale.get("t", {})
    
    result = translations.get(key)
    
    if result is None:
        # Try fallback parameter
        if fallback is not None:
            result = fallback
        # Try English fallback
        elif _current_language != "en_US" and "en_US" in _locales:
            en_locale = _locales["en_US"]
            result = en_locale.get("t", {}).get(key)
        
        # Last resort: return the key itself
        if result is None:
            result = key
            logger.debug(f"Translation missing: {key}")
    
    # Apply string interpolation if kwargs provided
    if kwargs:
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to format translation '{key}': {e}")
    
    return result


def get_language_name(lang_code: Optional[str] = None) -> str:
    """Get display name of a language"""
    if lang_code is None:
        lang_code = _current_language
    
    locale = _locales.get(lang_code, {})
    return locale.get("language_name", lang_code)


def get_available_languages() -> Dict[str, str]:
    """Get all available languages with their display names"""
    return {
        code: locale.get("language_name", code)
        for code, locale in _locales.items()
    }


# Auto-load locales on import
load_locales()

