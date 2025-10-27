"""
Configuration loader - Pure YAML

Handles loading and saving configuration from/to YAML files.
"""
from pathlib import Path
import yaml
from loguru import logger


def load_config_dict(config_path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        logger.info(f"Configuration loaded from {config_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def save_config_dict(config: dict, config_path: str = "config.yaml"):
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to config file
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise

