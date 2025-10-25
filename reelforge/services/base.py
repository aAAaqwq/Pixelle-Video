"""
Base service class for all capability services
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from reelforge.core.config_manager import ConfigManager


class BaseService(ABC):
    """
    Base service class for all capability services
    
    Provides callable interface and basic properties:
        - Direct call: result = await service(...)
        - Active capability: service.active
        - Available IDs: service.available
    
    Usage:
        result = await reelforge.llm("Hello world")
        print(f"Using: {reelforge.llm.active}")
        print(f"Available: {reelforge.llm.available}")
    """
    
    def __init__(self, config_manager: ConfigManager, capability_type: str):
        """
        Initialize service
        
        Args:
            config_manager: ConfigManager instance
            capability_type: Type of capability (llm, tts, etc.)
        """
        self._config_manager = config_manager
        self._capability_type = capability_type
    
    @abstractmethod
    async def __call__(self, **kwargs) -> Any:
        """
        Make service callable directly
        
        This is the main entry point for using the service.
        Subclasses MUST implement this with specific signatures.
        
        Example:
            answer = await reelforge.llm(prompt="Hello")
        """
        pass
    
    @property
    def active(self) -> Optional[str]:
        """
        Get active capability ID
        
        Returns:
            Active capability ID (e.g., "call") or None if not set
        
        Example:
            print(f"Using LLM: {reelforge.llm.active}")
        """
        return self._config_manager.get_active(self._capability_type)
    
    @property
    def available(self) -> list[str]:
        """
        List available capability IDs
        
        Returns:
            List of capability IDs
        
        Example:
            print(f"Available LLMs: {reelforge.llm.available}")
        """
        return self._config_manager.get_available_ids(self._capability_type)
    
    def __repr__(self) -> str:
        """String representation"""
        active = self.active or "none"
        available = ", ".join(self.available) if self.available else "none"
        return (
            f"<{self.__class__.__name__} "
            f"active={active!r} "
            f"available=[{available}]>"
        )

