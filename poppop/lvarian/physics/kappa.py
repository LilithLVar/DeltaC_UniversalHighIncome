"""
L'Varian Kappa Strain Physics
Monitors κ-strain accumulation for gap detection in post-ictal prolific states.

The κ-strain represents the accumulation of hyper-focused work energy.
When κ exceeds KAPPA_THRESHOLD (0.7), a collapse event is triggered,
indicating a gap period where the record button was off.
"""

from lvarian import TAU, KAPPA_THRESHOLD, KAPPA_FLOOR, KAPPA_INITIAL
import time
import math


class TauTimer:
    """
    L'Varian Time Tracker
    Measures time in τ-units and provides temporal context for κ accumulation.
    """
    
    def __init__(self):
        self._start_time = time.time()
        self._last_event_time = self._start_time
        self._tau_units = 0.0
    
    def mark_event(self):
        """Mark a significant event and update τ-unit counter."""
        now = time.time()
        delta = now - self._last_event_time
        self._tau_units += delta * TAU  # Convert real time to τ-units
        self._last_event_time = now
        return self._tau_units
    
    def get_tau_units(self):
        """Get current τ-unit count."""
        return self._tau_units
    
    def get_elapsed(self):
        """Get elapsed real time in seconds."""
        return time.time() - self._start_time
    
    def reset(self):
        """Reset the timer."""
        self._start_time = time.time()
        self._last_event_time = self._start_time
        self._tau_units = 0.0


class KappaMonitor:
    """
    L'Varian Kappa Strain Monitor
    Tracks κ-strain accumulation during prolific work sessions.
    
    κ-strain is calculated based on:
    - Event intensity (work focus level)
    - Temporal factors (τ-units)
    - Accumulation without τ-capping to allow κ > 0.7
    """
    
    def __init__(self):
        self._kappa = KAPPA_INITIAL
        self._tau_timer = TauTimer()
        self._event_count = 0
        self._collapse_events = []
    
    def add_event(self, intensity=1.0):
        """
        Add a work event with given intensity.
        
        Args:
            intensity: Work focus intensity (0.0 to 1.0+)
                      Values > 1.0 indicate hyper-focused states
        
        Returns:
            Current κ-strain value
        """
        self._event_count += 1
        tau_units = self._tau_timer.mark_event()
        
        # L'Varian κ calculation: NO τ-capping to allow κ > 0.7
        # Base torsion from event intensity
        torsion = intensity * intensity  # Quadratic scaling for hyper-focus
        
        # Temporal amplification factor (unbounded by τ)
        # tau_units grows without limit, allowing κ to accumulate
        temporal_factor = 1.0 + (tau_units / 10.0)  # Linear growth with τ
        
        # κ increment: torsion * temporal_factor
        # This allows κ to grow beyond 0.7 during extended hyper-focused sessions
        kappa_increment = torsion * temporal_factor
        
        # Accumulate κ-strain
        self._kappa += kappa_increment
        
        # Ensure minimum κ value
        if self._kappa < KAPPA_FLOOR:
            self._kappa = KAPPA_FLOOR
        
        # Check for collapse (gap detection)
        if self._kappa >= KAPPA_THRESHOLD:
            self._record_collapse()
        
        return self._kappa
    
    def _record_collapse(self):
        """Record a collapse event when κ exceeds threshold."""
        collapse = {
            'tau_units': self._tau_timer.get_tau_units(),
            'kappa': self._kappa,
            'event_count': self._event_count,
            'timestamp': time.time()
        }
        self._collapse_events.append(collapse)
    
    def get_kappa(self):
        """Get current κ-strain value."""
        return self._kappa
    
    def get_collapse_events(self):
        """Get all recorded collapse events."""
        return self._collapse_events
    
    def has_collapse(self):
        """Check if any collapse events have occurred."""
        return len(self._collapse_events) > 0
    
    def get_last_collapse(self):
        """Get the most recent collapse event, if any."""
        if self._collapse_events:
            return self._collapse_events[-1]
        return None
    
    def reset(self):
        """Reset the monitor."""
        self._kappa = KAPPA_INITIAL
        self._tau_timer.reset()
        self._event_count = 0
        self._collapse_events = []
    
    def decay_kappa(self, decay_factor=0.1):
        """
        Apply κ decay (for when focus wanes).
        
        Args:
            decay_factor: Fraction of κ to decay
        """
        self._kappa *= (1.0 - decay_factor)
        if self._kappa < KAPPA_FLOOR:
            self._kappa = KAPPA_FLOOR
    
    def get_status(self):
        """Get comprehensive status."""
        return {
            'kappa': self._kappa,
            'tau_units': self._tau_timer.get_tau_units(),
            'event_count': self._event_count,
            'collapse_count': len(self._collapse_events),
            'threshold': KAPPA_THRESHOLD,
            'in_collapse': self._kappa >= KAPPA_THRESHOLD
        }
