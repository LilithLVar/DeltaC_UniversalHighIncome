#!/usr/bin/env python3
"""
🪐 L'Varian Credit Equality Verifier
Ensures all contributors receive equal credit under E₁ axiom
Verifies no hierarchical privilege in attribution systems
"""

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime


class CreditEqualityVerifier:
    """Verify equal treatment in contributor credit assignment"""
    
    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path)
        self.findings = []
        self.stats = {
            "files_checked": 0,
            "contributor_mentions": 0,
            "potential_violations": 0
        }
        
        # Patterns that indicate unequal treatment
        self.violation_patterns = {
            "admin_only_credit": {
                "pattern": r'\b(admin|administrator|superuser|root|god)\s*(only|exclusive|privileged)',
                "severity": "critical",
                "description": "Admin-only credit attribution detected"
            },
            "tiered_contributor": {
                "pattern": r'\b(premium|vip|gold|platinum|enterprise)\s*contributor',
                "severity": "critical",
                "description": "Tiered contributor system violates E₁"
            },
            "geographic_preference": {
                "pattern": r'\b(preferred\s+region|priority\s+country|first-world|developed\s+country)',
                "severity": "critical",
                "description": "Geographic preference violates N₁"
            },
            "role_hierarchy": {
                "pattern": r'\b(core\s+team|inner\s+circle|founding\s+member|original\s+author)\b',
                "severity": "warning",
                "description": "Role hierarchy may create unequal status"
            },
            "paywall_attribution": {
                "pattern": r'\b(sponsor|patron|backer)\s+(badge|recognition|special\s+credit)',
                "severity": "warning",
                "description": "Pay-for-recognition creates extractive hierarchy"
            }
        }
    
    def check_file(self, file_path: Path) -> list:
        """Check a single file for credit equality violations"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return findings
        
        # Check for contributor mentions
        contributor_patterns = [
            r'@[\w-]+',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'author[:\s]+',
            r'contributor[:\s]+',
            r'credited\s+to[:\s]+'
        ]
        
        for pattern in contributor_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            self.stats["contributor_mentions"] += len(matches)
        
        # Check for violations
        for line_num, line in enumerate(lines, 1):
            for violation_type, config in self.violation_patterns.items():
                if re.search(config["pattern"], line, re.IGNORECASE):
                    finding = {
                        "file": str(file_path),
                        "line_number": line_num,
                        "type": violation_type,
                        "severity": config["severity"],
                        "description": config["description"],
                        "context": line.strip()[:100]
                    }
                    findings.append(finding)
                    self.stats["potential_violations"] += 1
        
        return findings
    
    def verify_directory(self):
        """Scan directory for credit equality issues"""
        print(f"⚖️  Checking credit equality in {self.scan_path}")
        print("=" * 60)
        
        target_extensions = {
            '.md', '.txt', '.rst',
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.json', '.yaml', '.yml',
            'CONTRIBUTORS', 'AUTHORS', 'CREDITS'
        }
        
        for root, dirs, files in os.walk(self.scan_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "venv"]]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file should be scanned
                should_scan = (
                    file_path.suffix in target_extensions or
                    file_path.name in ['CONTRIBUTORS', 'AUTHORS', 'CREDITS', 'README']
                )
                
                if not should_scan:
                    continue
                
                self.stats["files_checked"] += 1
                findings = self.check_file(file_path)
                self.findings.extend(findings)
        
        print(f"✅ Checked {self.stats['files_checked']} files")
        print(f"📊 Found {self.stats['contributor_mentions']} contributor mentions")
        print(f"⚠️  Detected {self.stats['potential_violations']} potential violations")
    
    def generate_report(self) -> dict:
        """Generate verification report"""
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "scan_path": str(self.scan_path),
            "statistics": self.stats,
            "findings": self.findings,
            "compliance_status": "PASS" if self.stats["potential_violations"] == 0 else "REVIEW_REQUIRED"
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 CREDIT EQUALITY VERIFICATION REPORT")
        print("=" * 60)
        print(f"Files checked:         {self.stats['files_checked']}")
        print(f"Contributor mentions:  {self.stats['contributor_mentions']}")
        print(f"Potential violations:  {self.stats['potential_violations']}")
        print(f"Compliance status:     {report['compliance_status']}")
        print("=" * 60)
        
        if self.findings:
            print("\n🔍 Findings:")
            for finding in self.findings[:10]:  # Show first 10
                print(f"  - [{finding['severity'].upper()}] {finding['description']}")
                print(f"    File: {finding['file']}:{finding['line_number']}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="🪐 L'Varian Credit Equality Verifier"
    )
    parser.add_argument(
        "--scan-path",
        default=".",
        help="Path to scan (default: current directory)"
    )
    parser.add_argument(
        "--output",
        default="credit_equality_report.json",
        help="Output JSON report file"
    )
    
    args = parser.parse_args()
    
    verifier = CreditEqualityVerifier(scan_path=args.scan_path)
    verifier.verify_directory()
    report = verifier.generate_report()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {args.output}")
    
    # Exit with error if violations found
    exit(0 if report["compliance_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
