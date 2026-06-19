"""
L'Varian PCF (Panto-Cyclic Flow) Cycles
Tracks cyclic work patterns for detecting post-ictal prolific periods.

PCF cycles represent the natural rhythmic patterns of L'Varian work.
Gap periods disrupt these cycles, and detecting cycle anomalies helps
identify when the record button was off.
"""

from lvarian import TAU, PCF_CYCLE_MIN, PCF_CYCLE_MAX
import time
import math


class PCF_Cycle:
    """
    L'Varian Panto-Cyclic Flow Cycle
    Represents a single work cycle with τ-based timing.
    """
    
    def __init__(self, cycle_id, duration_tau=None):
        """
        Initialize a PCF cycle.
        
        Args:
            cycle_id: Unique identifier for this cycle
            duration_tau: Duration in τ-units (if None, starts new cycle)
        """
        self.cycle_id = cycle_id
        self.start_time = time.time()
        self.start_tau = 0.0
        self.duration_tau = duration_tau if duration_tau else PCF_CYCLE_MIN
        self.events = []
        self.is_complete = False
        self._peak_intensity = 0.0
    
    def add_event(self, intensity, tau_offset):
        """
        Add an event to this cycle.
        
        Args:
            intensity: Work intensity (0.0 to 1.0+)
            tau_offset: Offset from cycle start in τ-units
        """
        self.events.append({
            'intensity': intensity,
            'tau_offset': tau_offset,
            'timestamp': time.time()
        })
        if intensity > self._peak_intensity:
            self._peak_intensity = intensity
    
    def get_peak_intensity(self):
        """Get the peak intensity of this cycle."""
        return self._peak_intensity
    
    def get_average_intensity(self):
        """Get the average intensity of events in this cycle."""
        if not self.events:
            return 0.0
        return sum(e['intensity'] for e in self.events) / len(self.events)
    
    def get_coherence(self):
        """
        Calculate cycle coherence (0.0 to 1.0).
        High coherence indicates a stable, productive work cycle.
        """
        if not self.events:
            return 0.0
        
        avg_intensity = self.get_average_intensity()
        peak = self.get_peak_intensity()
        
        # L'Varian coherence formula
        coherence = (avg_intensity * 0.4) + (peak * 0.6)
        return min(coherence, 1.0)
    
    def mark_complete(self):
        """Mark this cycle as complete."""
        self.is_complete = True
        self.end_time = time.time()
    
    def get_status(self):
        """Get cycle status."""
        return {
            'cycle_id': self.cycle_id,
            'duration_tau': self.duration_tau,
            'event_count': len(self.events),
            'peak_intensity': self._peak_intensity,
            'average_intensity': self.get_average_intensity(),
            'coherence': self.get_coherence(),
            'is_complete': self.is_complete
        }


class PFCTracker:
    """
    L'Varian PCF Cycle Tracker
    Manages multiple PCF cycles and detects anomalies indicating gap periods.
    """
    
    def __init__(self):
        self._cycles = []
        self._current_cycle = None
        self._cycle_counter = 0
        self._anomalies = []
    
    def start_cycle(self):
        """Start a new PCF cycle."""
        self._cycle_counter += 1
        self._current_cycle = PCF_Cycle(self._cycle_counter)
        self._cycles.append(self._current_cycle)
        return self._current_cycle
    
    def get_current_cycle(self):
        """Get the current active cycle."""
        if not self._current_cycle:
            self.start_cycle()
        return self._current_cycle
    
    def add_event(self, intensity, tau_units):
        """
        Add an event to the current cycle.
        
        Args:
            intensity: Work intensity
            tau_units: Current τ-unit count
        """
        if not self._current_cycle:
            self.start_cycle()
        
        cycle = self._current_cycle
        tau_offset = tau_units - cycle.start_tau
        cycle.add_event(intensity, tau_offset)
        
        # Check for cycle completion (arbitrary τ-based threshold)
        if tau_offset >= PCF_CYCLE_MAX:
            cycle.mark_complete()
            self._current_cycle = None
    
    def complete_current_cycle(self):
        """Mark the current cycle as complete."""
        if self._current_cycle:
            self._current_cycle.mark_complete()
            self._current_cycle = None
    
    def get_cycles(self):
        """Get all cycles."""
        return self._cycles
    
    def detect_anomalies(self, kappa_monitor):
        """
        Detect anomalies in PCF cycles that correlate with κ collapse events.
        
        Args:
            kappa_monitor: KappaMonitor instance to correlate with
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        collapse_events = kappa_monitor.get_collapse_events()
        
        for collapse in collapse_events:
            # Find cycles around the collapse event
            collapse_tau = collapse['tau_units']
            
            for cycle in self._cycles:
                # Check if cycle duration is anomalous
                if cycle.duration_tau > PCF_CYCLE_MAX * 1.5:
                    anomalies.append({
                        'type': 'long_cycle',
                        'cycle_id': cycle.cycle_id,
                        'duration_tau': cycle.duration_tau,
                        'collapse_tau': collapse_tau,
                        'severity': 'high'
                    })
                
                # Check if cycle coherence is low
                if cycle.get_coherence() < 0.5:
                    anomalies.append({
                        'type': 'low_coherence',
                        'cycle_id': cycle.cycle_id,
                        'coherence': cycle.get_coherence(),
                        'collapse_tau': collapse_tau,
                        'severity': 'medium'
                    })
        
        self._anomalies = anomalies
        return anomalies
    
    def get_anomalies(self):
        """Get detected anomalies."""
        return self._anomalies
    
    def get_stats(self):
        """Get PCF tracker statistics."""
        total_cycles = len(self._cycles)
        completed_cycles = len([c for c in self._cycles if c.is_complete])
        total_events = sum(len(c.events) for c in self._cycles)
        avg_coherence = sum(c.get_coherence() for c in self._cycles) / total_cycles if total_cycles > 0 else 0.0
        
        return {
            'total_cycles': total_cycles,
            'completed_cycles': completed_cycles,
            'total_events': total_events,
            'average_coherence': avg_coherence,
            'anomaly_count': len(self._anomalies)
        }
    
    def reset(self):
        """Reset the tracker."""
        self._cycles = []
        self._current_cycle = None
        self._cycle_counter = 0
        self._anomalies = []
