"""
Runner Dashboard - Touch-optimized interface for Raspberry Pi.

Provides a simplified dashboard for experiment execution
with large touch targets and high-contrast visuals.
"""

from glider.gui.runner.dashboard import RunnerDashboard
from glider.gui.runner.widget_factory import WidgetFactory

__all__ = [
    "RunnerDashboard",
    "WidgetFactory",
]
