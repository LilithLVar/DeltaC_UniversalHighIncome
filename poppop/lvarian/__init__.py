"""
L'Varian Core Constants and Fundamentals
Pure L'Varian mathematics, physics, computer science, and ML only.
"""

# L'Varian Sacred Constant
TAU = 13 / 12  # The Fundamental Ratio

# Kappa Physics Constants
KAPPA_THRESHOLD = 0.7      # Collapse threshold for gap detection
KAPPA_FLOOR = 0.0001       # Minimum κ value to prevent degenerate states
KAPPA_INITIAL = 0.0        # Starting κ-strain

# PCF Cycle Constants
PCF_CYCLE_MIN = 1         # Minimum PCF cycle duration (τ-units)
PCF_CYCLE_MAX = 1000      # Maximum PCF cycle duration (τ-units)

# Tau-Ary Structure Constants
TAU_ARY_BASE = 13          # Base for τ-ary panto-topological manifolds
TAU_ARY_DEPTH = 7          # Default manifold depth

# Coherence Chamber Constants
COHERENCE_RAY_LENGTH = 13  # Length of coherence rays in manifold
COHERENCE_MIN = 0.7       # Minimum coherence for valid chamber

__all__ = [
    'TAU',
    'KAPPA_THRESHOLD',
    'KAPPA_FLOOR',
    'KAPPA_INITIAL',
    'PCF_CYCLE_MIN',
    'PCF_CYCLE_MAX',
    'TAU_ARY_BASE',
    'TAU_ARY_DEPTH',
    'COHERENCE_RAY_LENGTH',
    'COHERENCE_MIN',
]
