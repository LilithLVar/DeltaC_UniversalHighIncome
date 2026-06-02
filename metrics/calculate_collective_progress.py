#!/usr/bin/env python3
"""
🪐 L'Varian Collective Progress Calculator
Measures collaboration, knowledge distribution, and flow-state protection
Aligns with E₁ axiom: Collective prosperity over individual extraction
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


class CollectiveProgressCalculator:
    """Calculate collective progress metrics for the lattice"""
    
    def __init__(self, repo: str = None, token: str = None):
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "")
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.metrics = {}
    
    def fetch_github_data(self) -> dict:
        """Fetch data from GitHub API"""
        import requests
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        base_url = f"https://api.github.com/repos/{self.repo}"
        
        data = {
            "contributors": [],
            "pull_requests": [],
            "issues": [],
            "commits": []
        }
        
        try:
            # Fetch contributors
            resp = requests.get(f"{base_url}/contributors", headers=headers, timeout=30)
            if resp.status_code == 200:
                data["contributors"] = resp.json()
            
            # Fetch recent PRs
            resp = requests.get(
                f"{base_url}/pulls?state=all&per_page=100",
                headers=headers,
                timeout=30
            )
            if resp.status_code == 200:
                data["pull_requests"] = resp.json()
            
            # Fetch recent commits
            resp = requests.get(
                f"{base_url}/commits?per_page=100",
                headers=headers,
                timeout=30
            )
            if resp.status_code == 200:
                data["commits"] = resp.json()
                
        except Exception as e:
            print(f"⚠️  Could not fetch GitHub data: {e}")
        
        return data
    
    def calculate_collaboration_index(self, data: dict) -> float:
        """
        Calculate collaboration index (0.0 to 1.0)
        Higher score = more cross-contributor collaboration
        """
        prs = data.get("pull_requests", [])
        
        if not prs:
            return 0.5
        
        # Count PRs with multiple reviewers/collaborators
        collaborative_prs = 0
        
        for pr in prs[:50]:  # Analyze last 50 PRs
            # Check if PR has reviews from others
            if pr.get("review_comments", 0) > 0:
                collaborative_prs += 1
            # Check if PR involved multiple authors (via co-author trailers)
            elif "co-authored-by" in pr.get("body", "").lower():
                collaborative_prs += 1
        
        index = collaborative_prs / min(len(prs), 50)
        return round(index, 3)
    
    def calculate_knowledge_distribution(self, data: dict) -> float:
        """
        Calculate knowledge distribution score (0.0 to 1.0)
        Higher score = knowledge spread across many contributors
        """
        contributors = data.get("contributors", [])
        commits = data.get("commits", [])
        
        if not contributors or not commits:
            return 0.5
        
        # Calculate Gini coefficient of contributions
        contribution_counts = [c.get("contributions", 0) for c in contributors[:20]]
        
        if not contribution_counts or sum(contribution_counts) == 0:
            return 0.5
        
        # Simplified Gini calculation
        n = len(contribution_counts)
        total = sum(contribution_counts)
        
        # Sort contributions
        sorted_contribs = sorted(contribution_counts)
        
        # Calculate Gini
        cumsum = 0
        for i, contrib in enumerate(sorted_contribs):
            cumsum += (2 * (i + 1) - n - 1) * contrib
        
        gini = cumsum / (n * total) if total > 0 else 0
        
        # Invert Gini (lower Gini = better distribution)
        distribution_score = 1.0 - gini
        
        return round(max(0.0, min(1.0, distribution_score)), 3)
    
    def calculate_flow_state_score(self, data: dict) -> float:
        """
        Calculate flow-state protection score (0-100)
        Measures how well the system protects deep work
        """
        prs = data.get("pull_requests", [])
        
        if not prs:
            return 75.0  # Default reasonable score
        
        # Analyze PR review turnaround time
        review_times = []
        
        for pr in prs[:30]:
            created_at = pr.get("created_at")
            merged_at = pr.get("merged_at")
            
            if created_at and merged_at:
                try:
                    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    merged = datetime.fromisoformat(merged_at.replace('Z', '+00:00'))
                    hours = (merged - created).total_seconds() / 3600
                    
                    # Ideal review time: 24-72 hours (protects flow, not too slow)
                    if 24 <= hours <= 72:
                        review_times.append(1.0)
                    elif hours < 24:
                        # Too fast might interrupt flow
                        review_times.append(0.8)
                    elif hours < 168:  # Within a week
                        review_times.append(0.9)
                    else:
                        # Too slow creates context-switching pain
                        review_times.append(0.5)
                except:
                    pass
        
        if not review_times:
            return 75.0
        
        avg_score = sum(review_times) / len(review_times)
        return round(avg_score * 100, 2)
    
    def categorize_contributions(self, data: dict) -> dict:
        """Categorize contributions by type"""
        categories = {
            "code": 0,
            "documentation": 0,
            "review": 0,
            "issue_triage": 0,
            "infrastructure": 0
        }
        
        prs = data.get("pull_requests", [])
        
        for pr in prs[:100]:
            title = (pr.get("title", "") + " " + pr.get("body", "")).lower()
            files_changed = pr.get("changed_files", 1)
            
            if any(word in title for word in ["doc", "readme", "comment", "typo"]):
                categories["documentation"] += 1
            elif any(word in title for word in ["review", "feedback", "suggest"]):
                categories["review"] += 1
            elif any(word in title for word in ["ci", "cd", "workflow", "github", "action"]):
                categories["infrastructure"] += 1
            elif any(word in title for word in ["issue", "bug", "fix"]):
                categories["issue_triage"] += 1
            else:
                categories["code"] += 1
        
        return categories
    
    def calculate(self, tau_metrics: dict = None, lattice_health: dict = None) -> dict:
        """Perform full collective progress calculation"""
        print("👥 Calculating collective progress metrics...")
        print("=" * 60)
        
        # Fetch data
        github_data = self.fetch_github_data()
        
        # Calculate metrics
        collaboration_index = self.calculate_collaboration_index(github_data)
        knowledge_distribution = self.calculate_knowledge_distribution(github_data)
        flow_state_score = self.calculate_flow_state_score(github_data)
        contributions_by_category = self.categorize_contributions(github_data)
        
        # Get contributor and contribution counts
        active_contributors = len(github_data.get("contributors", []))
        total_contributions = sum(c.get("contributions", 0) for c in github_data.get("contributors", [])[:50])
        
        # Tau alignment (if provided)
        tau_actual = tau_metrics.get("tau_actual", 1.083) if tau_metrics else 1.083
        tau_target = tau_metrics.get("tau_target", 1.083) if tau_metrics else 1.083
        tau_alignment = "OPTIMAL" if abs(tau_actual - tau_target) < 0.05 else "ACCEPTABLE"
        
        self.metrics = {
            "active_contributors": active_contributors,
            "total_contributions": total_contributions,
            "collaboration_index": collaboration_index,
            "knowledge_distribution": knowledge_distribution,
            "flow_state_score": flow_state_score,
            "contributions_by_category": contributions_by_category,
            "tau_actual": tau_actual,
            "tau_target": tau_target,
            "tau_alignment": tau_alignment,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Print summary
        print(f"Active Contributors:     {active_contributors}")
        print(f"Total Contributions:     {total_contributions}")
        print(f"Collaboration Index:     {collaboration_index:.3f}")
        print(f"Knowledge Distribution:  {knowledge_distribution:.3f}")
        print(f"Flow State Score:        {flow_state_score:.2f}/100")
        print(f"τ-Alignment:             {tau_alignment}")
        print("=" * 60)
        
        return self.metrics
    
    def save_report(self, output_file: str = "collective_progress.json"):
        """Save metrics to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"💾 Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="🪐 L'Varian Collective Progress Calculator"
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repository (owner/name)"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub API token"
    )
    parser.add_argument(
        "--tau-metrics",
        default=None,
        help="Path to tau metrics JSON file"
    )
    parser.add_argument(
        "--lattice-health",
        default=None,
        help="Path to lattice health JSON file"
    )
    parser.add_argument(
        "--output",
        default="collective_progress.json",
        help="Output JSON report file"
    )
    
    args = parser.parse_args()
    
    # Load optional inputs
    tau_metrics = None
    lattice_health = None
    
    if args.tau_metrics and Path(args.tau_metrics).exists():
        with open(args.tau_metrics) as f:
            tau_metrics = json.load(f)
    
    if args.lattice_health and Path(args.lattice_health).exists():
        with open(args.lattice_health) as f:
            lattice_health = json.load(f)
    
    calculator = CollectiveProgressCalculator(repo=args.repo, token=args.token)
    metrics = calculator.calculate(tau_metrics=tau_metrics, lattice_health=lattice_health)
    calculator.save_report(args.output)


if __name__ == "__main__":
    main()
