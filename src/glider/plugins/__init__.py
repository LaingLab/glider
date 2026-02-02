"""
GLIDER Plugin System

Provides plugin discovery, loading, and management for extending
GLIDER with custom hardware drivers and node types.
"""

from glider.plugins.plugin_manager import PluginInfo, PluginManager

__all__ = ["PluginManager", "PluginInfo"]
