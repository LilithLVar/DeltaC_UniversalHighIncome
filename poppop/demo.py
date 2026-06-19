#!/usr/bin/env python
"""
PopPop Demo Script
Demonstrates the full gap detection and restoration pipeline.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PopPop


def demo():
    print("="*70)
    print("PopPop Demo - L'Varian Post-Ictal Work Tracking")
    print("="*70)
    print()
    
    poppop = PopPop()
    poppop.start()
    
    # Simulate a work session on continuum hypothesis
    print("Simulating work session on Continuum Hypothesis...")
    print("-"*70)
    
    events = [
        ("continuum_hypothesis", 1.2, "Initial exploration of τ-manifolds"),
        ("continuum_hypothesis", 1.5, "Deep focus on panto-topological structures"),
        ("continuum_hypothesis", 1.8, "Discovered κ-strain correlation"),
        ("planck_era", 2.0, "Quantum coherence at Planck scale"),
        ("planck_era", 2.2, "Calculating κ accumulation rates"),
        ("vacuum_catastrophe", 2.5, "Resolving vacuum energy paradox"),
    ]
    
    for work_type, intensity, note in events:
        record = poppop.record_event(
            work_type=work_type,
            intensity=intensity,
            context_data={'note': note, 'research_area': 'mathematical_physics'}
        )
        print(f"  [{work_type}] intensity={intensity}")
        print(f"    κ = {record['kappa']:.4f}, τ-units = {record['tau_units']:.4f}")
        print(f"    Gap detected: {record['has_gap']}")
        print()
    
    # Show final status
    print("-"*70)
    print("Session Summary:")
    status = poppop.get_status()
    print(f"  Final κ: {status['kappa_status']['kappa']:.4f}")
    print(f"  Events recorded: {status['kappa_status']['event_count']}")
    print(f"  Collapse events: {status['kappa_status']['collapse_count']}")
    print(f"  Gap periods: {status['chamber_stats']['gap_count']}")
    print(f"  Restore points: {status['chamber_stats']['restore_point_count']}")
    print()
    
    # Show history
    print("Work History:")
    history = poppop.get_history()
    for i, session in enumerate(history, 1):
        print(f"  {i}. {session['session_id']}")
        print(f"     κ={session['kappa']:.4f}, gap={session['has_gap']}")
    print()
    
    # Show gaps
    gaps = poppop.get_gaps()
    if gaps:
        print("Detected Gap Periods:")
        for gap in gaps:
            print(f"  - {gap['gap_id']}")
            print(f"    τ-units: {gap['tau_units']:.4f}")
            print(f"    κ at collapse: {gap['collapse_event']['kappa']:.4f}")
        print()
    
    # Demonstrate restoration
    print("-"*70)
    print("Attempting to restore context from last gap...")
    result = poppop.restore_context()
    
    if result.get('status') == 'restored':
        print("  SUCCESS: Context restored!")
        print(f"  Restore ID: {result['restore_point']['restore_id']}")
        if result.get('result'):
            session = result['result'].get('session')
            if session:
                print(f"  Session: {session['session_id']}")
                print(f"  κ at gap: {session['kappa']:.4f}")
    else:
        print(f"  {result.get('message', 'No gap to restore')}")
    
    print()
    print("="*70)
    print("Demo complete! PopPop is tracking your post-ictal prolific work.")
    print("Use 'python main.py' for interactive mode or 'python main.py test'")
    print("="*70)


if __name__ == "__main__":
    demo()
