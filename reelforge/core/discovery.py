"""
Capability Registry System

Registers built-in capabilities from FastMCP tools.
"""

from typing import Any

from fastmcp import FastMCP
from loguru import logger

from reelforge.core.conventions import CapabilityInfo, parse_tool_name


class CapabilityRegistry:
    """
    Built-in capability registry
    
    Registers capabilities from local FastMCP tools
    based on tool naming convention.
    
    Simplified from CapabilityDiscovery - no external MCP support.
    If you need custom capabilities, add them to reelforge/capabilities/
    """
    
    def __init__(self, local_mcp: FastMCP):
        self.local_mcp = local_mcp
        self.capabilities: dict[str, dict[str, CapabilityInfo]] = {}
        # Structure: {type: {id: CapabilityInfo}}
    
    async def register_all(self):
        """Register all built-in capabilities"""
        logger.info("📦 Registering built-in capabilities...")
        
        # Get all tools from FastMCP server (returns dict: {name: FunctionTool})
        tools_dict = await self.local_mcp.get_tools()
        
        for tool_name, tool in tools_dict.items():
            capability_info = self._parse_capability(tool_name=tool_name, tool=tool)
            
            if capability_info:
                self._register_capability(capability_info)
        
        self._print_summary()
    
    def _parse_capability(
        self, tool_name: str, tool: Any
    ) -> CapabilityInfo | None:
        """
        Parse a tool into CapabilityInfo
        
        Key logic: Parse type and id from tool_name!
        """
        # Parse tool name following convention
        parsed = parse_tool_name(tool_name)
        if not parsed:
            # Not a capability tool (doesn't follow convention)
            return None
        
        capability_type, capability_id = parsed
        
        # Extract optional metadata from meta.reelforge
        reelforge_meta = {}
        if hasattr(tool, "meta") and tool.meta:
            reelforge_meta = tool.meta.get("reelforge", {})
        
        # Build CapabilityInfo
        return CapabilityInfo(
            type=capability_type,
            id=capability_id,
            tool_name=tool_name,
            display_name=reelforge_meta.get("display_name"),
            description=reelforge_meta.get("description")
            or (tool.description if hasattr(tool, "description") else None),
            is_default=reelforge_meta.get("is_default", False),
            tool=tool,
        )
    
    def _register_capability(self, capability_info: CapabilityInfo):
        """Register a capability"""
        cap_type = capability_info.type
        cap_id = capability_info.id
        
        # Initialize type dict if needed
        if cap_type not in self.capabilities:
            self.capabilities[cap_type] = {}
        
        # Check for duplicates
        if cap_id in self.capabilities[cap_type]:
            existing = self.capabilities[cap_type][cap_id]
            logger.warning(
                f"  ⚠️  Duplicate capability: {cap_type}/{cap_id} - keeping first registration"
            )
            return
        
        # Register
        self.capabilities[cap_type][cap_id] = capability_info
        
        # Log
        logger.info(f"  ✓ {cap_type}/{cap_id} ({capability_info.display_label})")
    
    def _print_summary(self):
        """Print registration summary"""
        logger.info("\n📊 Registered Capabilities:")
        
        if not self.capabilities:
            logger.info("  No capabilities registered")
            return
        
        for cap_type in sorted(self.capabilities.keys()):
            logger.info(f"\n  {cap_type}:")
            
            for cap_id, cap_info in self.capabilities[cap_type].items():
                default_marker = " [DEFAULT]" if cap_info.is_default else ""
                
                logger.info(
                    f"    • {cap_id} ({cap_info.display_label}){default_marker}"
                )

