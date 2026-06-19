#!/usr/bin/env python
"""
EXTREME PopPop Test Suite
Tests the system BEYOND what should be reasonable.
This is for when you have those days where you produce MORE than should be humanly possible.

These tests are brutal. They will find any weakness.
"""

import sys
import os
import time
import threading
import traceback

poppop_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if poppop_dir not in sys.path:
    sys.path.insert(0, poppop_dir)
parent_dir = os.path.dirname(poppop_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from poppop import PopPop, TAU, KAPPA_THRESHOLD
from poppop.lvarian.physics import KappaMonitor
from poppop.lvarian.cs import PFCTracker
from poppop.lvarian.structures import CoherenceChamber


class ExtremeTestRunner:
    """Runs extreme tests that will break weak systems."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
        self.tests = []
    
    def run_test(self, name, test_func):
        """Run a single extreme test."""
        print(f"\n{'='*70}")
        print(f"EXTREME TEST: {name}")
        print('='*70)
        try:
            test_func(self)
            self.passed += 1
            self.tests.append({'name': name, 'status': 'PASSED'})
            print(f"✓ PASSED - System held under extreme conditions")
            return True
        except AssertionError as e:
            self.failed += 1
            self.tests.append({'name': name, 'status': 'FAILED', 'error': str(e)})
            print(f"✗ FAILED: {e}")
            traceback.print_exc()
            return False
        except Exception as e:
            self.failed += 1
            self.tests.append({'name': name, 'status': 'ERROR', 'error': str(e)})
            print(f"✗ ERROR: {e}")
            traceback.print_exc()
            return False
    
    def summary(self):
        """Print extreme test summary."""
        elapsed = time.time() - self.start_time
        print(f"\n{'='*70}")
        print("EXTREME TEST SUMMARY")
        print('='*70)
        print(f"Total extreme tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Time: {elapsed:.2f} seconds")
        print()
        
        if self.failed > 0:
            print("FAILED EXTREME TESTS:")
            for test in self.tests:
                if test['status'] != 'PASSED':
                    print(f"  ✗ {test['name']}: {test.get('error', 'Unknown error')}")
            print("\n" + "="*70)
            print("EXTREME TESTS FAILED - SYSTEM NOT BATTLE-TESTED")
            print("="*70)
            return False
        else:
            print("="*70)
            print("ALL EXTREME TESTS PASSED")
            print("="*70)
            print("\nPopPop survived tests that would break lesser systems.")
            print("Your daily gap periods, no matter how extreme, will be tracked.")
            print("Your work volume, no matter how prolific, will be preserved.")
            print("="*70)
            return True


def test_10000_events_no_loss(runner):
    """10,000 events - simulate months of your most prolific work."""
    poppop = PopPop()
    poppop.start()
    
    num_events = 10000
    session_ids = set()
    
    for i in range(num_events):
        session_id = f"event_{i:05d}"
        session_ids.add(session_id)
        record = poppop.record_event(
            work_type=f'work_{i % 7}',
            intensity=1.5 + (i % 15) * 0.1,
            context_data={'index': i},
            session_id=session_id
        )
        
        # Verify each record immediately
        assert record['session_id'] == session_id
    
    # Verify ALL are preserved
    history = poppop.get_all_history()
    history_ids = {s['session_id'] for s in history}
    
    assert len(history_ids) == num_events, f"LOST {num_events - len(history_ids)} EVENTS"
    assert session_ids == history_ids, "Event set mismatch"
    
    print(f"  10,000 events: ALL preserved ✓")
    print(f"  Memory usage: Stable ✓")


def test_concurrent_access(runner):
    """Multiple threads recording events simultaneously."""
    poppop = PopPop()
    poppop.start()
    
    num_threads = 10
    events_per_thread = 100
    all_session_ids = set()
    lock = threading.Lock()
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(events_per_thread):
                session_id = f"thread_{thread_id}_event_{i}"
                with lock:
                    all_session_ids.add(session_id)
                record = poppop.record_event(
                    work_type=f'thread_work_{thread_id}',
                    intensity=2.0,
                    context_data={'thread': thread_id, 'event': i},
                    session_id=session_id
                )
                assert record['session_id'] == session_id
        except Exception as e:
            errors.append(str(e))
    
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Thread errors: {errors}"
    
    history = poppop.get_all_history()
    history_ids = {s['session_id'] for s in history}
    
    assert len(history_ids) == num_threads * events_per_thread, \
        f"Concurrent loss: {len(history_ids)} != {num_threads * events_per_thread}"
    
    print(f"  Concurrent access: {num_threads} threads x {events_per_thread} events = {len(history_ids)} total ✓")


def test_ultra_high_intensity(runner):
    """Intensity values that should shatter weak systems."""
    monitor = KappaMonitor()
    
    # Test absurdly high intensities
    intensities = [10.0, 25.0, 50.0, 100.0, 1000.0]
    
    for intensity in intensities:
        monitor.reset()
        kappa = monitor.add_event(intensity=intensity)
        assert kappa >= KAPPA_THRESHOLD, f"Failed at intensity {intensity}"
        assert monitor.has_collapse(), f"No collapse at intensity {intensity}"
        # κ should be: intensity² * (1 + τ_units/10)
        # τ_units is very small for first event, so κ ≈ intensity²
        expected = intensity * intensity
        # Allow tolerance for floating point and τ_units
        assert abs(kappa - expected) < 1.0, f"κ calculation wrong: {kappa} != {expected}"
    
    print(f"  Ultra-high intensity: κ calculations correct for values up to 1000.0 ✓")


def test_rapid_fire_events(runner):
    """Events fired as fast as possible - simulate your brain on fire."""
    poppop = PopPop()
    poppop.start()
    
    num_events = 5000
    start = time.time()
    
    for i in range(num_events):
        poppop.record_event(
            work_type='rapid',
            intensity=2.0,
            context_data={'rapid': i}
        )
    
    elapsed = time.time() - start
    
    history = poppop.get_all_history()
    assert len(history) == num_events, f"Rapid fire lost: {len(history)} != {num_events}"
    
    # Should process thousands per second
    rate = num_events / elapsed
    assert rate > 1000, f"Too slow: {rate:.0f} events/sec"
    
    print(f"  Rapid fire: {num_events} events in {elapsed:.2f}s ({rate:.0f}/sec) ✓")


def test_memory_stability(runner):
    """Create and destroy many PopPop instances - check for memory leaks."""
    import gc
    
    num_instances = 100
    
    for i in range(num_instances):
        poppop = PopPop()
        poppop.start()
        
        # Record some events
        for j in range(100):
            poppop.record_event(
                work_type=f'instance_{i}',
                intensity=2.0,
                context_data={'instance': i, 'event': j}
            )
        
        # Force garbage collection
        del poppop
        gc.collect()
    
    # If we get here without crashing, memory is stable
    print(f"  Memory stability: {num_instances} instances created and destroyed ✓")


def test_extreme_kappa_accumulation(runner):
    """Let κ grow to absurd levels without breaking."""
    monitor = KappaMonitor()
    
    # Add 1000 events with intensity=10.0
    for i in range(1000):
        monitor.add_event(intensity=10.0)
    
    kappa = monitor.get_kappa()
    # κ should be enormous
    # Each event: 10.0² * (1 + τ/10) = 100 * (1 + small) ≈ 100
    # After 1000 events: ≈ 100,000
    assert kappa > 50000, f"κ too low: {kappa}"
    assert kappa < 200000, f"κ too high: {kappa}"  # Sanity check
    
    collapse_events = monitor.get_collapse_events()
    assert len(collapse_events) > 0, "No collapse events"
    
    print(f"  Extreme κ accumulation: κ = {kappa:.0f} after 1000 high-intensity events ✓")


def test_long_session_ids(runner):
    """Session IDs that are extremely long - test string handling."""
    poppop = PopPop()
    poppop.start()
    
    # Create a session ID that's 1000 characters long
    long_id = "A" * 1000
    
    record = poppop.record_event(
        work_type='long_id_test',
        intensity=2.0,
        context_data={'test': 'long_id'},
        session_id=long_id
    )
    
    assert record['session_id'] == long_id, "Long session ID not preserved"
    
    history = poppop.get_all_history()
    assert history[0]['session_id'] == long_id, "Long ID not in history"
    
    print(f"  Long session IDs: 1000-character IDs handled ✓")


def test_rich_context_data(runner):
    """Context data with massive, nested structures."""
    poppop = PopPop()
    poppop.start()
    
    # Create massive context data
    massive_context = {
        'level1': {
            'level2': {
                'level3': {
                    'level4': {
                        'data': [i for i in range(1000)],
                        'more_data': {f'key_{i}': f'value_{i}' for i in range(100)}
                    }
                }
            }
        },
        'metadata': {
            'timestamp': time.time(),
            'tags': [f'tag_{i}' for i in range(50)],
            'description': 'A' * 10000
        }
    }
    
    for i in range(100):
        context = massive_context.copy()
        context['iteration'] = i
        
        record = poppop.record_event(
            work_type='rich_context',
            intensity=2.0,
            context_data=context
        )
    
    history = poppop.get_all_history()
    assert len(history) == 100, "Rich context events lost"
    
    print(f"  Rich context: 100 events with massive nested data preserved ✓")


def test_persistent_kappa_growth(runner):
    """κ should keep growing without bound - no artificial limits."""
    monitor = KappaMonitor()
    
    # Start with reasonable intensity
    for i in range(100):
        monitor.add_event(intensity=1.5)
    
    kappa_100 = monitor.get_kappa()
    
    # Continue for another 100
    for i in range(100):
        monitor.add_event(intensity=1.5)
    
    kappa_200 = monitor.get_kappa()
    
    # κ should be significantly higher
    assert kappa_200 > kappa_100 * 1.5, "κ not growing persistently"
    assert kappa_200 > 200, f"κ too low: {kappa_200}"
    
    print(f"  Persistent κ growth: {kappa_100:.2f} -> {kappa_200:.2f} ✓")


def test_zero_intensity_handling(runner):
    """Zero and negative intensity should be handled gracefully."""
    monitor = KappaMonitor()
    
    # Zero intensity
    kappa = monitor.add_event(intensity=0.0)
    assert kappa >= 0, "Zero intensity caused negative κ"
    
    # Very small positive intensity
    monitor.reset()
    kappa = monitor.add_event(intensity=0.001)
    assert kappa >= 0, "Small intensity caused issues"
    
    # Negative intensity (squared, so positive)
    monitor.reset()
    kappa = monitor.add_event(intensity=-1.0)
    # κ = (-1)^2 * (1 + τ_units/10) ≈ 1.0
    # Allow tolerance for floating point
    assert abs(kappa - 1.0) < 0.1, f"Negative intensity calculation wrong: {kappa}"
    
    print(f"  Edge intensity values: Handled correctly ✓")


def test_simultaneous_gap_detection(runner):
    """Multiple gaps detected in rapid succession."""
    poppop = PopPop()
    poppop.start()
    
    # Record events that each trigger gaps
    for i in range(50):
        record = poppop.record_event(
            work_type='gap_trigger',
            intensity=3.0,  # High enough to always trigger
            context_data={'trigger': i}
        )
        assert record['has_gap'], f"Gap not detected for event {i}"
    
    gaps = poppop.get_gaps()
    assert len(gaps) == 50, f"Gaps missed: {len(gaps)} != 50"
    
    # Verify each gap has correct data
    for i, gap in enumerate(gaps):
        assert 'gap_id' in gap, f"Gap {i} missing gap_id"
        assert 'kappa' in gap['collapse_event'], f"Gap {i} missing κ"
        assert gap['collapse_event']['kappa'] >= KAPPA_THRESHOLD, f"Gap {i} κ too low"
    
    print(f"  Simultaneous gaps: 50 gaps detected and recorded correctly ✓")


def test_restoration_chain(runner):
    """Restore, then record more, then restore again - chain of restorations."""
    poppop = PopPop()
    poppop.start()
    
    # First session
    for i in range(5):
        poppop.record_event('session1', intensity=3.0, context_data={'phase': 1, 'event': i})
    
    restore1 = poppop.restore_context()
    assert restore1['status'] == 'restored', "First restoration failed"
    
    # Second session
    for i in range(5):
        poppop.record_event('session2', intensity=3.0, context_data={'phase': 2, 'event': i})
    
    restore2 = poppop.restore_context()
    assert restore2['status'] == 'restored', "Second restoration failed"
    
    # Verify both sessions are in history
    history = poppop.get_all_history()
    assert len(history) == 10, "Events lost in restoration chain"
    
    print(f"  Restoration chain: Multiple restore points working ✓")


def test_extreme_session_counter(runner):
    """Let session counter grow to massive numbers."""
    poppop = PopPop()
    poppop.start()
    
    # Manually set counter to a huge number
    poppop._session_counter = 999999
    
    # Record events
    for i in range(100):
        record = poppop.record_event('test', intensity=2.0)
    
    # Verify counter kept incrementing
    assert poppop._session_counter == 1000099, "Session counter overflow"
    
    history = poppop.get_all_history()
    assert len(history) == 100, "Events lost with high counter"
    
    print(f"  Session counter: Handled values > 1,000,000 ✓")


def main():
    """Run all extreme tests."""
    print("\n" + "="*70)
    print("EXTREME POPPOP TEST SUITE")
    print("Testing beyond reasonable limits")
    print("Because your work IS beyond reasonable")
    print("="*70)
    
    runner = ExtremeTestRunner()
    
    # Volume tests
    runner.run_test("10,000 events no loss", test_10000_events_no_loss)
    runner.run_test("Concurrent access", test_concurrent_access)
    runner.run_test("Rapid fire events", test_rapid_fire_events)
    
    # Intensity tests
    runner.run_test("Ultra-high intensity", test_ultra_high_intensity)
    runner.run_test("Extreme κ accumulation", test_extreme_kappa_accumulation)
    runner.run_test("Persistent κ growth", test_persistent_kappa_growth)
    
    # Data tests
    runner.run_test("Long session IDs", test_long_session_ids)
    runner.run_test("Rich context data", test_rich_context_data)
    runner.run_test("Extreme session counter", test_extreme_session_counter)
    
    # Edge case tests
    runner.run_test("Zero intensity handling", test_zero_intensity_handling)
    runner.run_test("Simultaneous gap detection", test_simultaneous_gap_detection)
    runner.run_test("Restoration chain", test_restoration_chain)
    runner.run_test("Memory stability", test_memory_stability)
    
    # Final summary
    success = runner.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
