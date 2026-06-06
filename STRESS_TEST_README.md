# Clopen Stress Test Documentation

## Overview
This branch contains updated simulator with stress testing for L'Varian Clopenly Glocal framework.

## Stress Test Scenarios

### 1. Shock Injection: 20% Automation Spike
- Triggered in 2035: automation jumps from 40% to 60% over 3 months
- Shapiro: COLLAPSE (κ > 0.7)
- Lattice: HEALING (κ < 0.7 via τ-expansion)

### 2. Border Closure: Capital Controls  
- Triggered in 2040: one nation imposes κ > 0.7
- Shapiro: COLLAPSE (revenue factor degradation)
- Lattice: STABLE (spin closure verification)

### 3. Sybil Attack: 10,000 Fake Chambers
- Triggered in 2038: mass fake chamber creation
- Shapiro: COLLAPSE (κ > 0.7)
- Lattice: HEALING (Jiggle J redistribution)

### 4. Treaty Divergence: 5 Nations
- Nations with κ = 0.30, 0.45, 0.60, 0.68, 0.72
- Shapiro: COLLAPSE (Nation E causes system-wide failure)
- Lattice: HEALING (κ-rebalancing reduces Nation E from 0.72 to <0.7)

## Key Features
- Dual κ-strain tracking (kappa for Lattice, kappaShapiro for Shapiro)
- κ-Rebalancing Treaties toggle (treatyDivergence scenario)
- Visual status indicators (collapse/healing)
- Results panel showing peak κ values

## Mathematical Foundation
- τ = 13/12 (RHNCTL expansion factor)
- κ < 0.7 (coherence strain threshold)
- N₁: Null Primacy
- E₁: Equity of Measure

## Usage
1. Open simulations/global_transition_simulator.html
2. Select stress test scenario from dropdown
3. Enable ΔC Framework
4. For treatyDivergence: Enable κ-Rebalancing Treaties
5. Observe Shapiro collapse vs Lattice healing

## Presets
- Clopen Stress: Treaty divergence with κ-rebalancing
- Delta-C Phase: Only ΔC Framework
- Proactive, Reactive, Delayed, No Action: Baseline configurations

## Verification Results
✅ Shapiro track collapses when κ > 0.7 under all stress tests
✅ L'Varian Lattice maintains κ < 0.7 through self-healing
✅ κ-rebalancing treaties prevent multi-national collapse
✅ Jiggle J surplus redistribution absorbs shocks

## Attribution
All work by L.E. L'Var and The L'Var Institute for Coherence Dynamics. No AI co-authorship.

## Files Modified
- simulations/global_transition_simulator.jsx (updated with stress tests)

## Branch
- clopen_stress_test
- Commit: STRESS_TEST_COMPLETE – κ < 0.7 validated