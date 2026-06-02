#!/usr/bin/env python3
"""
🪐 L'Varian Kappa-Strain Analyzer
Measures system harmony under automation pressure
κ = (AutomationVelocity × ContributorCount) / SynchronizationCapacity
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


class KappaStrainAnalyzer:
    """Analyze κ-strain coefficient for repository health"""
    
    def __init__(self, sha: str = None):
        self.sha = sha
        self.metrics = {
            "automation_velocity": 0.0,
            "contributor_count": 0,
            "synchronization_capacity": 0.0,
            "kappa_strain": 0.0,
            "strain_status": "UNKNOWN"
        }
        
        # Thresholds
        self.thresholds = {
            "healthy": 0.5,
            "warning": 0.75,
            "critical": 1.0
        }
    
    def get_open_prs(self) -> int:
        """Get count of open pull requests"""
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--state", "open", "--json", "number"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                return len(prs)
        except Exception as e:
            print(f"⚠️  Could not fetch PRs: {e}")
        return 0
    
    def get_open_issues(self) -> int:
        """Get count of open issues"""
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--state", "open", "--json", "number"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                return len(issues)
        except Exception as e:
            print(f"⚠️  Could not fetch issues: {e}")
        return 0
    
    def get_contributor_count(self) -> int:
        """Get unique contributor count"""
        try:
            result = subprocess.run(
                ["git", "log", "--format=%ae"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                emails = set(result.stdout.strip().split('\n'))
                return len([e for e in emails if e])
        except Exception as e:
            print(f"⚠️  Could not fetch contributors: {e}")
        return 5  # Default estimate
    
    def calculate_automation_velocity(self) -> float:
        """Calculate automation coverage (0.0 to 1.0)"""
        # Check for workflow files
        workflow_dir = Path(".github/workflows")
        
        if not workflow_dir.exists():
            return 0.2
        
        workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        
        # Base score from workflow presence
        base_score = min(0.5, len(workflow_files) * 0.1)
        
        # Check for test workflows
        has_tests = any("test" in wf.name.lower() for wf in workflow_files)
        test_bonus = 0.2 if has_tests else 0.0
        
        # Check for security workflows
        has_security = any("security" in wf.name.lower() or "hygiene" in wf.name.lower() 
                          for wf in workflow_files)
        security_bonus = 0.2 if has_security else 0.0
        
        # Check for metrics workflows
        has_metrics = any("metric" in wf.name.lower() or "tau" in wf.name.lower() 
                         for wf in workflow_files)
        metrics_bonus = 0.1 if has_metrics else 0.0
        
        velocity = base_score + test_bonus + security_bonus + metrics_bonus
        return min(1.0, velocity)
    
    def calculate_synchronization_capacity(self) -> float:
        """Calculate system's capacity to synchronize changes"""
        # Factors affecting synchronization:
        # - Number of active maintainers
        # - Review turnaround time
        # - CI/CD pipeline efficiency
        # - Documentation quality
        
        base_capacity = 5.0  # Baseline capacity
        
        # Check for CODEOWNERS
        if Path("CODEOWNERS").exists() or Path(".github/CODEOWNERS").exists():
            base_capacity += 2.0
        
        # Check for CONTRIBUTING guide
        if Path("CONTRIBUTING.md").exists():
            base_capacity += 1.0
        
        # Check for review templates
        review_template_dir = Path(".github/PULL_REQUEST_TEMPLATE")
        if review_template_dir.exists():
            base_capacity += 1.0
        
        # Estimate based on workflow automation
        automation = self.calculate_automation_velocity()
        base_capacity += automation * 2.0
        
        return base_capacity
    
    def analyze(self) -> dict:
        """Perform full κ-strain analysis"""
        print("🔬 Analyzing κ-strain coefficient...")
        print("=" * 60)
        
        # Gather metrics
        open_prs = self.get_open_prs()
        open_issues = self.get_open_issues()
        contributors = self.get_contributor_count()
        automation = self.calculate_automation_velocity()
        sync_capacity = self.calculate_synchronization_capacity()
        
        print(f"Open PRs:              {open_prs}")
        print(f"Open Issues:           {open_issues}")
        print(f"Contributors:          {contributors}")
        print(f"Automation Velocity:   {automation:.2f}")
        print(f"Synchronization Cap:   {sync_capacity:.2f}")
        
        # Calculate κ-strain
        # Formula: κ = (automation_gap * 0.4) + (backlog * 0.3) + (coverage_gap * 0.3)
        automation_gap = 1.0 - automation
        backlog = (open_prs * 0.05) + (open_issues * 0.02)
        coverage_gap = max(0, 1.0 - (automation * 0.8))
        
        kappa = (automation_gap * 0.4) + (backlog * 0.3) + (coverage_gap * 0.3)
        
        # Determine status
        if kappa > self.thresholds["critical"]:
            status = "CRITICAL"
        elif kappa > self.thresholds["warning"]:
            status = "WARNING"
        elif kappa > self.thresholds["healthy"]:
            status = "CAUTION"
        else:
            status = "HEALTHY"
        
        self.metrics = {
            "automation_velocity": round(automation, 3),
            "contributor_count": contributors,
            "synchronization_capacity": round(sync_capacity, 3),
            "open_prs": open_prs,
            "open_issues": open_issues,
            "kappa_strain": round(kappa, 3),
            "strain_status": status,
            "thresholds": self.thresholds,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print("\n" + "=" * 60)
        print(f"κ-STRAIN RESULT: {kappa:.3f} ({status})")
        print("=" * 60)
        
        return self.metrics
    
    def generate_github_output(self):
        """Generate GitHub Actions output format"""
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"kappa_strain={self.metrics['kappa_strain']}\n")
                f.write(f"strain_status={self.metrics['strain_status']}\n")
                f.write(f"automation_velocity={self.metrics['automation_velocity']}\n")
                f.write(f"contributor_count={self.metrics['contributor_count']}\n")
            
            print("✅ GitHub outputs written")
    
    def save_report(self, output_file: str = "kappa_strain_report.json"):
        """Save analysis report to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"💾 Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="🪐 L'Varian Kappa-Strain Analyzer"
    )
    parser.add_argument(
        "--sha",
        default=None,
        help="Git commit SHA to analyze"
    )
    parser.add_argument(
        "--output",
        default="kappa_strain_report.json",
        help="Output JSON report file"
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Write to GITHUB_OUTPUT for Actions"
    )
    
    args = parser.parse_args()
    
    analyzer = KappaStrainAnalyzer(sha=args.sha)
    metrics = analyzer.analyze()
    
    if args.github_output:
        analyzer.generate_github_output()
    
    analyzer.save_report(args.output)
    
    # Exit with error if critical strain
    exit(0 if metrics["strain_status"] != "CRITICAL" else 1)


if __name__ == "__main__":
    main()
