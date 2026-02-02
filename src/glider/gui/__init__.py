"""
GLIDER GUI Shell

The PyQt6 application that provides the visual interface.
Acts as the View and Controller in the MVC paradigm.

Supports two distinct modes:
- Desktop Mode: Full IDE with dockable widgets and node graph editing
- Runner Mode: Touch-optimized dashboard for Raspberry Pi (480x800)
"""

from glider.gui.main_window import MainWindow
from glider.gui.view_manager import ViewManager, ViewMode

__all__ = [
    "MainWindow",
    "ViewManager",
    "ViewMode",
]
