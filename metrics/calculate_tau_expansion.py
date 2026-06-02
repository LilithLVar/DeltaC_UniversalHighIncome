#!/usr/bin/env python3
"""
🪐 L'Varian τ-Expansion Calculator
Calculates the tau expansion rate of the contributor lattice.

τ = (contributions_current_period / contributions_previous_period)
Target τ = 13/12 ≈ 1.083333 (natural expansion rate)

This measures whether the lattice is growing at a sustainable, natural pace.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    from github import Github
except ImportError:
    print("⚠️  PyGithub not installed. Run: pip install PyGithub")
    sys.exit(1)


def calculate_tau_expansion(repo_name: str, token: str, days_period: int = 30) -> dict:
    """
    Calculate τ-expansion rate for a repository.
    
    Args:
        repo_name: Repository name (owner/repo)
        token: GitHub API token
        days_period: Number of days per period
    
    Returns:
        Dictionary containing τ metrics
    """
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    now = datetime.utcnow()
    current_start = now - timedelta(days=days_period)
    previous_start = current_start - timedelta(days=days_period)
    
    # Count contributions in current period
    current_contributions = 0
    current_contributors = set()
    
    # Count contributions in previous period
    previous_contributions = 0
    previous_contributors = set()
    
    # Get commits for current period
    current_commits = repo.get_commits(since=current_start)
    for commit in current_commits:
        current_contributions += 1
        if commit.author:
            current_contributors.add(commit.author.login)
    
    # Get commits for previous period
    previous_commits = repo.get_commits(since=previous_start, until=current_start)
    for commit in previous_commits:
        previous_contributions += 1
        if commit.author:
            previous_contributors.add(commit.author.login)
    
    # Calculate τ
    if previous_contributions > 0:
        tau_actual = current_contributions / previous_contributions
    else:
        tau_actual = float('inf') if current_contributions > 0 else 1.0
    
    tau_target = 13/12  # ≈ 1.083333
    
    # Calculate deviation from target
    tau_deviation = abs(tau_actual - tau_target)
    
    # Determine expansion status
    if tau_deviation < 0.05:
        expansion_status = "OPTIMAL"
        status_emoji = "🟢"
    elif tau_deviation < 0.15:
        expansion_status = "ACCEPTABLE"
        status_emoji = "🟡"
    elif tau_actual > tau_target + 0.5:
        expansion_status = "OVEREXPANDED"
        status_emoji = "🟠"
    elif tau_actual < tau_target - 0.3:
        expansion_status = "UNDEREXPANDED"
        status_emoji = "🔵"
    else:
        expansion_status = "SUBOPTIMAL"
        status_emoji = "🔴"
    
    return {
        "@context": "https://lvarian.org/metrics/v1",
        "@type": "TauExpansionMetrics",
        "timestamp": now.isoformat() + "Z",
        "repository": repo_name,
        "period_days": days_period,
        "current_period": {
            "start": current_start.isoformat() + "Z",
            "end": now.isoformat() + "Z",
            "contributions": current_contributions,
            "contributors": len(current_contributors),
            "contributor_list": list(current_contributors)[:20]  # Top 20
        },
        "previous_period": {
            "start": previous_start.isoformat() + "Z",
            "end": current_start.isoformat() + "Z",
            "contributions": previous_contributions,
            "contributors": len(previous_contributors),
            "contributor_list": list(previous_contributors)[:20]
        },
        "tau_actual": round(tau_actual, 6),
        "tau_target": round(tau_target, 6),
        "tau_deviation": round(tau_deviation, 6),
        "expansion_status": expansion_status,
        "status_emoji": status_emoji,
        "interpretation": get_tau_interpretation(tau_actual, tau_target, expansion_status)
    }


def get_tau_interpretation(tau_actual: float, tau_target: float, status: str) -> str:
    """Generate human-readable interpretation of τ value."""
    if status == "OPTIMAL":
        return "🌟 The lattice is expanding at the perfect natural rate (13/12). Sustainable growth achieved."
    elif status == "ACCEPTABLE":
        return "✅ Growth is within acceptable range. Minor adjustments may optimize further."
    elif status == "OVEREXPANDED":
        return "⚠️ Rapid expansion detected. Risk of κ-strain increase. Consider slowing pace."
    elif status == "UNDEREXPANDED":
        return "📉 Growth is below natural rate. May need exploration initiatives or new contributors."
    else:
        return "🔄 Growth pattern needs attention. Review collaboration and exploration mechanisms."


def main():
    parser = argparse.ArgumentParser(description="Calculate τ-expansion rate")
    parser.add_argument("--repo", type=str, required=True, help="Repository name (owner/repo)")
    parser.add_argument("--token", type=str, required=True, help="GitHub API token")
    parser.add_argument("--days", type=int, default=30, help="Days per period (default: 30)")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"🌀 Calculating τ-expansion for {args.repo}...")
    print(f"   Period: {args.days} days")
    
    try:
        metrics = calculate_tau_expansion(args.repo, args.token, args.days)
        
        print(f"\n## τ-Expansion Results")
        print(f"   Current Period Contributions: {metrics['current_period']['contributions']}")
        print(f"   Previous Period Contributions: {metrics['previous_period']['contributions']}")
        print(f"   Current Contributors: {metrics['current_period']['contributors']}")
        print(f"   Previous Contributors: {metrics['previous_period']['contributors']}")
        print(f"\n   τ Actual: {metrics['tau_actual']}")
        print(f"   τ Target: {metrics['tau_target']} (13/12)")
        print(f"   Deviation: {metrics['tau_deviation']}")
        print(f"   Status: {metrics['status_emoji']} {metrics['expansion_status']}")
        print(f"\n   {metrics['interpretation']}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\n💾 Metrics saved to: {args.output}")
        else:
            print("\n\nFull JSON:")
            print(json.dumps(metrics, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error calculating τ-expansion: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
