"""
PopPop - L'Varian Daemon for Post-Ictal Prolific Work Tracking

Pure L'Varian implementation tracking work during absence seizure gap periods.
Only uses L'Varian mathematics, physics, computer science, and ML.

Usage:
    python main.py status    - Show current tracking status
    python main.py history   - Show work history and detected gaps
    python main.py restore   - Restore context from last gap
    python main.py test      - Run self-test to verify gap detection
"""

import sys
import os
import time
import json
from datetime import datetime

# Add poppop to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lvarian import TAU, KAPPA_THRESHOLD
from lvarian.physics import KappaMonitor, TauTimer
from lvarian.cs import PFCTracker
from lvarian.structures import CoherenceChamber


class PopPop:
    """
    Main PopPop Daemon
    
    Tracks post-ictal prolific work and restores context when the
    record button switches back on after gap periods.
    """
    
    VERSION = "1.0.0-lvarian"
    
    def __init__(self):
        """Initialize PopPop with L'Varian components."""
        self.kappa_monitor = KappaMonitor()
        self.pcf_tracker = PFCTracker()
        self.coherence_chamber = CoherenceChamber()
        
        self._running = False
        self._session_counter = 0
        self._last_session_id = None
    
    def start(self):
        """Start the PopPop daemon."""
        self._running = True
        print(f"PopPop v{self.VERSION} started - L'Varian tracking active")
        print(f"  τ = {TAU:.4f}")
        print(f"  κ_threshold = {KAPPA_THRESHOLD}")
    
    def stop(self):
        """Stop the PopPop daemon."""
        self._running = False
        print("PopPop daemon stopped")
    
    def record_event(self, work_type="work", intensity=1.0, context_data=None, session_id=None):
        """
        Record a work event.
        
        Args:
            work_type: Type of work (e.g., "continuum", "planck", "vacuum")
            intensity: Focus intensity (1.0 = normal, >1.0 = hyper-focused)
            context_data: Additional context to save
            session_id: Optional custom session ID (if None, auto-generated)
        
        Returns:
            Event record with status
        """
        if context_data is None:
            context_data = {}
        
        # Generate session ID if not provided
        if session_id is None:
            self._session_counter += 1
            session_id = f"session_{self._session_counter}_{int(time.time())}"
        self._last_session_id = session_id
        
        # Add context metadata
        context_data.update({
            'work_type': work_type,
            'intensity': intensity,
            'session_id': session_id,
            'timestamp': time.time(),
            'tau_time': datetime.now().isoformat()
        })
        
        # Record with KappaMonitor (κ accumulation)
        kappa = self.kappa_monitor.add_event(intensity)
        
        # Record with PFCTracker
        tau_units = self.kappa_monitor._tau_timer.get_tau_units()
        self.pcf_tracker.add_event(intensity, tau_units)
        
        # Record with CoherenceChamber
        node = self.coherence_chamber.record_work(
            session_id=session_id,
            context_data=context_data,
            kappa_monitor=self.kappa_monitor,
            pcf_tracker=self.pcf_tracker
        )
        
        event_record = {
            'session_id': session_id,
            'work_type': work_type,
            'intensity': intensity,
            'kappa': kappa,
            'tau_units': tau_units,
            'has_gap': self.kappa_monitor.has_collapse(),
            'node_id': node.node_id if node else None
        }
        
        return event_record
    
    def get_status(self):
        """Get current PopPop status."""
        kappa_status = self.kappa_monitor.get_status()
        pcf_stats = self.pcf_tracker.get_stats()
        chamber_stats = self.coherence_chamber.get_stats()
        
        return {
            'poppop_version': self.VERSION,
            'running': self._running,
            'kappa_status': kappa_status,
            'pcf_stats': pcf_stats,
            'chamber_stats': chamber_stats,
            'last_session': self._last_session_id
        }
    
    def get_history(self, limit=None):
        """Get work history.
        
        Args:
            limit: Maximum number of sessions to return (None for all)
        
        Returns:
            All work sessions, or last 'limit' sessions if specified
        """
        sessions = self.coherence_chamber._work_sessions
        if limit is None:
            return sessions
        return sessions[-limit:]
    
    def get_all_history(self):
        """Get ALL work history - guaranteed complete, no truncation."""
        return self.get_history(limit=None)
    
    def get_gaps(self):
        """Get detected gap periods."""
        return self.coherence_chamber.get_gap_periods()
    
    def restore_context(self):
        """Restore context from last detected gap."""
        restore_point = self.coherence_chamber.get_last_restore_point()
        if not restore_point:
            return {
                'status': 'no_gap_detected',
                'message': 'No gap periods recorded'
            }
        
        result = self.coherence_chamber.restore_context()
        return {
            'status': 'restored',
            'restore_point': restore_point,
            'result': result
        }
    
    def run_test(self):
        """
        Run self-test to verify gap detection pipeline.
        
        This test simulates a hyper-focused work session that should
        trigger κ > 0.7 and detect a gap period.
        """
        print("\n" + "="*60)
        print("PopPop Self-Test - Gap Detection Verification")
        print("="*60)
        
        # Reset all monitors
        self.kappa_monitor.reset()
        self.pcf_tracker.reset()
        self.coherence_chamber = CoherenceChamber('test')
        
        test_events = [
            # Simulate building up κ-strain
            {'work_type': 'continuum_hypothesis', 'intensity': 1.5, 'context': {'note': 'Initial exploration'}},
            {'work_type': 'continuum_hypothesis', 'intensity': 1.8, 'context': {'note': 'Deep focus on τ-manifolds'}},
            {'work_type': 'planck_era', 'intensity': 2.0, 'context': {'note': 'Quantum coherence analysis'}},
            {'work_type': 'planck_era', 'intensity': 2.2, 'context': {'note': 'κ-strain calculations'}},
            {'work_type': 'vacuum_catastrophe', 'intensity': 2.5, 'context': {'note': 'Hyper-focused resolution'}},
            {'work_type': 'vacuum_catastrophe', 'intensity': 2.5, 'context': {'note': 'Critical insight - κ should exceed 0.7'}},
        ]
        
        print("\nSimulating work events (intensity > 1.0 = hyper-focus)...")
        print("-"*60)
        
        gap_detected = False
        for i, event in enumerate(test_events, 1):
            record = self.record_event(
                work_type=event['work_type'],
                intensity=event['intensity'],
                context_data=event['context']
            )
            
            print(f"Event {i}: {event['work_type']} (intensity={event['intensity']})")
            print(f"  κ = {record['kappa']:.6f}")
            print(f"  τ-units = {record['tau_units']:.4f}")
            print(f"  Gap detected: {record['has_gap']}")
            
            if record['has_gap']:
                gap_detected = True
                print(f"  >>> COLLAPSE DETECTED! κ >= {KAPPA_THRESHOLD}")
            print()
        
        # Final status
        status = self.get_status()
        print("-"*60)
        print("Final Status:")
        print(f"  Current κ: {status['kappa_status']['kappa']:.6f}")
        print(f"  Collapse count: {status['kappa_status']['collapse_count']}")
        print(f"  Gap periods: {len(self.get_gaps())}")
        print(f"  Restore points: {status['chamber_stats']['restore_point_count']}")
        
        # Verify test passed
        print("\n" + "="*60)
        if gap_detected and status['kappa_status']['kappa'] >= KAPPA_THRESHOLD:
            print("TEST PASSED: Gap detection working correctly!")
            print(f"  κ successfully exceeded threshold ({KAPPA_THRESHOLD})")
            print(f"  Collapse events recorded: {status['kappa_status']['collapse_count']}")
            
            # Show restore capability
            restore = self.restore_context()
            if restore.get('restore_point'):
                print(f"  Restore point available: {restore['restore_point']['restore_id']}")
                print("  Context can be restored from gap period")
            
            return True
        else:
            print("TEST FAILED: κ did not reach threshold")
            print(f"  Final κ: {status['kappa_status']['kappa']:.6f}")
            print(f"  Threshold: {KAPPA_THRESHOLD}")
            print("\n  This indicates κ calculation needs adjustment")
            print("  Current formula: κ += intensity² * (1 + τ_units/10)")
            print("  This allows unbounded growth, but test events may need")
            print("  higher intensity or more events to reach threshold")
            return False
    
    def interactive_mode(self):
        """Run PopPop in interactive mode."""
        self.start()
        print("\nInteractive mode - Enter commands:")
        print("  event <type> <intensity> - Record work event")
        print("  status - Show current status")
        print("  history - Show work history")
        print("  gaps - Show detected gaps")
        print("  restore - Restore from last gap")
        print("  test - Run self-test")
        print("  quit - Exit")
        
        while self._running:
            try:
                command = input("\npoppop> ").strip()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    self.stop()
                    break
                
                elif cmd == 'event':
                    if len(parts) >= 3:
                        work_type = parts[1]
                        try:
                            intensity = float(parts[2])
                            context = {}
                            if len(parts) > 3:
                                context['note'] = ' '.join(parts[3:])
                            record = self.record_event(work_type, intensity, context)
                            print(f"Event recorded: κ={record['kappa']:.4f}, gap={record['has_gap']}")
                        except ValueError:
                            print("Invalid intensity. Use a number.")
                    else:
                        print("Usage: event <type> <intensity> [note]")
                
                elif cmd == 'status':
                    status = self.get_status()
                    print(f"κ: {status['kappa_status']['kappa']:.4f}")
                    print(f"Collapse: {status['kappa_status']['in_collapse']}")
                    print(f"Sessions: {status['chamber_stats']['session_count']}")
                    print(f"Gaps: {status['chamber_stats']['gap_count']}")
                
                elif cmd == 'history':
                    sessions = self.get_history(10)
                    for s in sessions:
                        print(f"{s['session_id']}: κ={s['kappa']:.4f}, gap={s['has_gap']}")
                
                elif cmd == 'gaps':
                    gaps = self.get_gaps()
                    if gaps:
                        for g in gaps:
                            print(f"{g['gap_id']}: τ={g['tau_units']:.2f}")
                    else:
                        print("No gaps detected")
                
                elif cmd == 'restore':
                    result = self.restore_context()
                    if result.get('status') == 'restored':
                        print("Context restored successfully!")
                    else:
                        print(result.get('message', 'No gap to restore from'))
                
                elif cmd == 'test':
                    self.run_test()
                
                else:
                    print(f"Unknown command: {cmd}")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point."""
    poppop = PopPop()
    
    if len(sys.argv) < 2:
        # No arguments - run interactive mode
        poppop.interactive_mode()
    else:
        command = sys.argv[1].lower()
        
        if command == 'status':
            poppop.start()
            status = poppop.get_status()
            print(json.dumps(status, indent=2))
        
        elif command == 'history':
            poppop.start()
            history = poppop.get_history()
            print(json.dumps(history, indent=2))
        
        elif command == 'restore':
            poppop.start()
            result = poppop.restore_context()
            print(json.dumps(result, indent=2))
        
        elif command == 'test':
            poppop.start()
            passed = poppop.run_test()
            sys.exit(0 if passed else 1)
        
        elif command == 'interactive' or command == 'i':
            poppop.interactive_mode()
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python main.py [status|history|restore|test|interactive]")
            sys.exit(1)


if __name__ == "__main__":
    main()
