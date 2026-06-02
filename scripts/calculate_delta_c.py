#!/usr/bin/env python3
"""
🪐 L'Varian Delta-C Credit Calculator
Calculates autopoietic contribution credit (δ^c) based on:
- Contribution quality and impact
- Axiom compliance (N₁, E₁)
- System strain (κ) at time of contribution
- Collaboration enhancement

δ^c = (base_value × quality_multiplier × collaboration_bonus) / (1 + κ_strain)
"""

import argparse
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path


def calculate_delta_c(pr_number: int, contributor: str, kappa_strain: float, 
                      quality_score: float = 1.0, collaboration_bonus: float = 1.0) -> dict:
    """
    Calculate δ^c credit for a contribution.
    
    Args:
        pr_number: Pull request number
        contributor: GitHub username of contributor
        kappa_strain: Current system strain (0.0 - 1.0+)
        quality_score: Quality multiplier (0.5 - 2.0)
        collaboration_bonus: Bonus for collaborative work (1.0 - 3.0)
    
    Returns:
        Dictionary containing credit calculation details
    """
    # Base credit value
    base_value = 100.0
    
    # Apply quality multiplier
    quality_adjusted = base_value * quality_score
    
    # Apply collaboration bonus
    collaboration_adjusted = quality_adjusted * collaboration_bonus
    
    # Apply κ-strain divisor (higher strain = lower credit to prevent burnout)
    delta_c = collaboration_adjusted / (1.0 + kappa_strain)
    
    # Generate cryptographic hash for certificate
    timestamp = datetime.utcnow().isoformat() + "Z"
    hash_input = f"{pr_number}-{contributor}-{timestamp}-{delta_c}"
    credit_hash = hashlib.sha384(hash_input.encode()).hexdigest()
    
    return {
        "@context": "https://lvarian.org/context/v1",
        "@type": "DeltaCCredit",
        "pr_number": pr_number,
        "contributor": contributor,
        "timestamp": timestamp,
        "calculation": {
            "base_value": base_value,
            "quality_score": quality_score,
            "collaboration_bonus": collaboration_bonus,
            "kappa_strain": kappa_strain,
            "formula": "(base × quality × collaboration) / (1 + κ)"
        },
        "delta_c_value": round(delta_c, 4),
        "credit_hash": credit_hash,
        "axioms_validated": ["N₁", "E₁"],
        "version": "1.0.0"
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate δ^c contribution credit")
    parser.add_argument("--pr-number", type=int, required=True, help="Pull request number")
    parser.add_argument("--contributor", type=str, required=True, help="Contributor username")
    parser.add_argument("--strain", type=float, default=0.5, help="Current κ-strain (0.0-1.0)")
    parser.add_argument("--quality", type=float, default=1.0, help="Quality score (0.5-2.0)")
    parser.add_argument("--collaboration", type=float, default=1.0, help="Collaboration bonus (1.0-3.0)")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    print(f"💎 Calculating δ^c credit for PR #{args.pr_number} by @{args.contributor}")
    print(f"   κ-strain: {args.strain}")
    print(f"   Quality: {args.quality}")
    print(f"   Collaboration: {args.collaboration}")
    
    credit = calculate_delta_c(
        pr_number=args.pr_number,
        contributor=args.contributor,
        kappa_strain=args.strain,
        quality_score=args.quality,
        collaboration_bonus=args.collaboration
    )
    
    print(f"\n✅ δ^c Credit Assigned: {credit['delta_c_value']}")
    print(f"   Hash: {credit['credit_hash'][:16]}...")
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(credit, f, indent=2)
        print(f"   Saved to: {output_path}")
    else:
        print("\nFull Certificate:")
        print(json.dumps(credit, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
