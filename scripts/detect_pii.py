#!/usr/bin/env python3
"""
🪐 L'Varian PII Detection Script
Advanced pattern matching for Personally Identifiable Information
Aligns with E₁ axiom: Equal protection for all human nodes
"""

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime


class PIIDetector:
    """Advanced PII detection with context-aware analysis"""
    
    def __init__(self, scan_path: str = ".", report_file: str = "pii_report.json"):
        self.scan_path = Path(scan_path)
        self.report_file = report_file
        self.findings = []
        self.stats = {
            "files_scanned": 0,
            "total_findings": 0,
            "critical": 0,
            "warning": 0,
            "notice": 0
        }
        
        # PII patterns with severity levels
        self.patterns = {
            "email": {
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "severity": "warning",
                "description": "Email address detected",
                "exclude": ["example.com", "test.local", "localhost", "placeholder"]
            },
            "phone_international": {
                "pattern": r'\+?[0-9]{1,3}[-.\s]?\(?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}',
                "severity": "warning",
                "description": "Phone number detected",
                "exclude": ["555", "000", "1234", "example"]
            },
            "ssn_us": {
                "pattern": r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b',
                "severity": "critical",
                "description": "Potential US Social Security Number",
                "exclude": []
            },
            "credit_card": {
                "pattern": r'\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b',
                "severity": "critical",
                "description": "Potential credit card number",
                "exclude": ["4111111111111111", "4242424242424242", "5500000000000004"]
            },
            "passport_us": {
                "pattern": r'\b[0-9]{9}\b',
                "severity": "warning",
                "description": "Potential passport number (9 digits)",
                "exclude": []
            },
            "ip_address": {
                "pattern": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                "severity": "notice",
                "description": "IP address detected",
                "exclude": ["0.0.0.0", "127.0.0.1", "255.255.255.255", "192.168.", "10."]
            },
            "date_of_birth": {
                "pattern": r'\b(0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b',
                "severity": "warning",
                "description": "Potential date of birth",
                "exclude": []
            },
            "bank_account": {
                "pattern": r'\b[0-9]{8,17}\b',
                "severity": "warning",
                "description": "Potential bank account number",
                "exclude": []
            }
        }
        
        # Files to exclude from scanning
        self.exclude_patterns = [
            "__pycache__",
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "vendor",
            "*.min.js",
            "*.map"
        ]
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning"""
        path_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern in path_str or path_str.endswith(pattern.lstrip("*")):
                return True
        return False
    
    def is_test_data(self, line: str) -> bool:
        """Check if line contains test data markers"""
        test_markers = [
            "test", "example", "dummy", "fake", "mock", 
            "sample", "placeholder", "todo", "fixme"
        ]
        line_lower = line.lower()
        return any(marker in line_lower for marker in test_markers)
    
    def scan_file(self, file_path: Path) -> list:
        """Scan a single file for PII"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return findings
        
        for line_num, line in enumerate(lines, 1):
            # Skip if likely test data
            if self.is_test_data(line):
                continue
            
            for pii_type, config in self.patterns.items():
                matches = re.finditer(config["pattern"], line, re.IGNORECASE)
                
                for match in matches:
                    matched_text = match.group()
                    
                    # Check exclusions
                    excluded = any(excl in matched_text for excl in config["exclude"])
                    
                    if not excluded:
                        finding = {
                            "file": str(file_path),
                            "line_number": line_num,
                            "type": pii_type,
                            "severity": config["severity"],
                            "description": config["description"],
                            "matched_text": matched_text[:20] + "..." if len(matched_text) > 20 else matched_text,
                            "context": line.strip()[:100]
                        }
                        findings.append(finding)
                        self.stats[config["severity"]] += 1
        
        return findings
    
    def scan_directory(self):
        """Recursively scan directory for PII"""
        print(f"🔍 Starting PII scan in {self.scan_path}")
        print("=" * 60)
        
        # File extensions to scan
        target_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.json', '.yaml', '.yml', '.xml',
            '.md', '.txt', '.rst', '.html',
            '.css', '.scss', '.java', '.go',
            '.rb', '.php', '.sh', '.bash'
        }
        
        for root, dirs, files in os.walk(self.scan_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(excl in d for excl in ["__pycache__", "node_modules", ".git", "venv"])]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check extension
                if file_path.suffix not in target_extensions:
                    continue
                
                # Check exclusions
                if self.should_exclude(file_path):
                    continue
                
                self.stats["files_scanned"] += 1
                findings = self.scan_file(file_path)
                self.findings.extend(findings)
        
        self.stats["total_findings"] = len(self.findings)
        print(f"✅ Scanned {self.stats['files_scanned']} files")
        print(f"📊 Found {self.stats['total_findings']} potential PII instances")
    
    def generate_report(self):
        """Generate JSON report of findings"""
        report = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "scan_path": str(self.scan_path),
            "statistics": self.stats,
            "findings": self.findings
        }
        
        # Write report
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {self.report_file}")
        
        # Print summary to stdout
        print("\n" + "=" * 60)
        print("📋 PII SCAN SUMMARY")
        print("=" * 60)
        print(f"Files scanned:     {self.stats['files_scanned']}")
        print(f"Total findings:    {self.stats['total_findings']}")
        print(f"  - Critical:      {self.stats['critical']}")
        print(f"  - Warning:       {self.stats['warning']}")
        print(f"  - Notice:        {self.stats['notice']}")
        print("=" * 60)
        
        # Exit with error if critical findings
        if self.stats['critical'] > 0:
            print("\n❌ CRITICAL PII VIOLATIONS DETECTED!")
            print("Review the report immediately.")
            return 1
        elif self.stats['warning'] > 0:
            print("\n⚠️  WARNING: Potential PII detected. Review recommended.")
            return 0
        else:
            print("\n✅ No critical PII violations found.")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="🪐 L'Varian PII Detection Scanner"
    )
    parser.add_argument(
        "--scan-path",
        default=".",
        help="Path to scan for PII (default: current directory)"
    )
    parser.add_argument(
        "--report-file",
        default="pii_report.json",
        help="Output file for JSON report (default: pii_report.json)"
    )
    
    args = parser.parse_args()
    
    detector = PIIDetector(
        scan_path=args.scan_path,
        report_file=args.report_file
    )
    
    detector.scan_directory()
    exit_code = detector.generate_report()
    
    exit(exit_code)


if __name__ == "__main__":
    main()
