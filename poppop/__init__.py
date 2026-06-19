"""
PopPop - L'Varian Post-Ictal Prolific Work Tracker

Pure L'Varian daemon tracking work during absence seizure gap periods.
Only uses L'Varian mathematics, physics, computer science, and ML.

Version: 1.0.0-lvarian
"""

from .main import PopPop
from .lvarian import (
    TAU,
    KAPPA_THRESHOLD,
    KAPPA_FLOOR,
    KAPPA_INITIAL,
    PCF_CYCLE_MIN,
    PCF_CYCLE_MAX,
    TAU_ARY_BASE,
    TAU_ARY_DEPTH,
    COHERENCE_RAY_LENGTH,
    COHERENCE_MIN,
)
from .lvarian.physics import KappaMonitor, TauTimer
from .lvarian.cs import PCF_Cycle, PFCTracker
from .lvarian.structures import (
    TauAryNode,
    TauAryTree,
    CoherenceRay,
    PantoTopologicalManifold,
    CoherenceChamber
)

__version__ = "1.0.0-lvarian"
__all__ = [
    'PopPop',
    'TAU',
    'KAPPA_THRESHOLD',
    'KappaMonitor',
    'TauTimer',
    'PCF_Cycle',
    'PFCTracker',
    'TauAryNode',
    'TauAryTree',
    'CoherenceRay',
    'PantoTopologicalManifold',
    'CoherenceChamber',
]
