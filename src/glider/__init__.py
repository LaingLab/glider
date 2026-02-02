"""
GLIDER - General Laboratory Interface for Design, Experimentation, and Recording

A modular experimental orchestration platform for laboratory hardware control
through visual flow-based programming.
"""

__version__ = "1.0.0"
__author__ = "LaingLab"

from glider.core.experiment_session import ExperimentSession
from glider.core.glider_core import GliderCore

__all__ = ["GliderCore", "ExperimentSession", "__version__"]
