"""
Configuration Manager

Manages capability configuration and provides unified access to MCP tools.
Simplified from Router - only handles config injection, no external routing.
"""

from typing import Any

from fastmcp import Client
from loguru import logger

from reelforge.core.conventions import CapabilityInfo


class ConfigManager:
    """
    Configuration manager for capabilities
    
    Core responsibilities:
    1. Manage active capability selection
    2. Inject configuration into capability calls
    3. Provide unified MCP client interface
    
    No external MCP routing - all capabilities are builtin.
    """
    
    def __init__(self, registry, config: dict):
        """
        Initialize config manager
        
        Args:
            registry: CapabilityRegistry instance with registered capabilities
            config: Application configuration dict
        """
        self.registry = registry
        self.config = config
        self._active: dict[str, str] = {}  # type -> id
        
        # Create in-memory MCP client for calling builtin capabilities
        self._local_client = Client(registry.local_mcp)
        
        self._load_active_from_config()
    
    def _load_active_from_config(self):
        """Load active capability selections from config"""
        for cap_type in self.registry.capabilities.keys():
            # Read active from flat structure: config[type]["default"]
            cap_section = self.config.get(cap_type, {})
            if isinstance(cap_section, dict):
                configured_id = cap_section.get("default")
                if configured_id and configured_id in self.registry.capabilities[cap_type]:
                    self._active[cap_type] = configured_id
                    continue
            
            # Otherwise, auto-select default
            self._auto_select_default(cap_type)
    
    def _auto_select_default(self, cap_type: str):
        """Auto-select default capability"""
        capabilities = self.registry.capabilities[cap_type]
        
        # Find default
        for cap_id, cap_info in capabilities.items():
            if cap_info.is_default:
                self._active[cap_type] = cap_id
                logger.info(f"✓ Auto-selected default {cap_type}: {cap_id}")
                return
        
        # No default, use first
        if capabilities:
            first_id = next(iter(capabilities.keys()))
            self._active[cap_type] = first_id
            logger.info(f"✓ Auto-selected first {cap_type}: {first_id}")
    
    def get_active(self, cap_type: str) -> str | None:
        """Get active capability ID for a type"""
        return self._active.get(cap_type)
    
    def get_available_ids(self, cap_type: str) -> list[str]:
        """Get available capability IDs for a type"""
        return list(self.registry.capabilities.get(cap_type, {}).keys())
    
    async def call(self, cap_type: str, cap_id: str | None = None, **kwargs) -> Any:
        """
        Call a capability with config injection
        
        Args:
            cap_type: Capability type (e.g., "llm", "tts")
            cap_id: Specific capability ID (defaults to active)
            **kwargs: Arguments for the capability
        
        Returns:
            Result from the capability
        """
        # Determine which capability to use
        if cap_id is None:
            cap_id = self.get_active(cap_type)
        
        if not cap_id:
            raise ValueError(f"No active capability for type: {cap_type}")
        
        # Get capability info
        cap_info = self.registry.capabilities[cap_type][cap_id]
        
        logger.debug(f"Calling {cap_info.full_id} ({cap_info.display_label})")
        
        # Prepare tool arguments with config injection
        tool_arguments = self._inject_config(cap_info, kwargs)
        
        # Call tool via MCP protocol using in-memory client
        async with self._local_client:
            result = await self._local_client.call_tool(
                name=cap_info.tool_name,
                arguments=tool_arguments
            )
        
        # Extract content from MCP result
        return self._extract_content(result)
    
    def _inject_config(self, cap_info: CapabilityInfo, kwargs: dict) -> dict:
        """
        Inject configuration into tool arguments
        
        This is the core value of ConfigManager - it handles config injection
        so individual capabilities don't need to know about config.yaml
        """
        tool_arguments = kwargs.copy()
        
        # Handle LLM-specific configuration (direct top-level config)
        if cap_info.type == "llm":
            llm_config = self.config.get("llm", {})
            
            # Add LLM credentials and settings (if not already provided)
            tool_arguments.setdefault("api_key", llm_config.get("api_key", ""))
            tool_arguments.setdefault("base_url", llm_config.get("base_url", ""))
            tool_arguments.setdefault("model", llm_config.get("model", ""))
            
            logger.debug(f"LLM using: {tool_arguments['model']} @ {tool_arguments['base_url']}")
        
        # Handle other capability types (image, tts, etc.)
        else:
            # Read capability-specific config from flat structure: config[type][id]
            cap_section = self.config.get(cap_info.type, {})
            if isinstance(cap_section, dict):
                cap_config = cap_section.get(cap_info.id, {})
                if isinstance(cap_config, dict):
                    # Merge config (don't override kwargs)
                    for key, value in cap_config.items():
                        tool_arguments.setdefault(key, value)
        
        return tool_arguments
    
    def _extract_content(self, result: Any) -> Any:
        """
        Extract content from MCP result
        
        MCP returns a CallToolResult with content field
        """
        if hasattr(result, 'content'):
            # Handle different content types
            if isinstance(result.content, list):
                # Multiple content items, join them
                return '\n'.join(
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                )
            else:
                return result.content
        
        # Fallback: return the result as-is
        return result

