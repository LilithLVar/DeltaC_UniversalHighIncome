#!/usr/bin/env python3
"""
🕸️ L'Varian Lattice Health Assessor
Evaluates the overall health of the contributor lattice based on:
- Contribution distribution (avoiding single points of failure)
- Collaboration patterns (cross-pollination vs silos)
- Knowledge sharing (documentation, comments, reviews)
- Flow state protection (uninterrupted work time)
- Axiom compliance (N₁, E₁ adherence)

Returns a health score 0-100 and detailed component scores.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

try:
    from github import Github
except ImportError:
    print("⚠️  PyGithub not installed. Run: pip install PyGithub")
    sys.exit(1)


def assess_lattice_health(repo_name: str, token: str, tau_metrics: dict = None) -> dict:
    """
    Assess overall lattice health.
    
    Args:
        repo_name: Repository name (owner/repo)
        token: GitHub API token
        tau_metrics: Optional τ-expansion metrics for context
    
    Returns:
        Dictionary containing health assessment
    """
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    # Get recent activity (last 90 days)
    since = datetime.utcnow() - timedelta(days=90)
    commits = list(repo.get_commits(since=since))
    pulls = list(repo.get_pulls(state='all', sort='created', direction='desc')[:200])
    issues = list(repo.get_issues(state='all', since=since)[:200])
    
    # Calculate component scores
    contribution_distribution = calc_contribution_distribution(commits)
    collaboration_patterns = calc_collaboration_patterns(pulls)
    knowledge_sharing = calc_knowledge_sharing(commits, issues)
    flow_state_protection = calc_flow_state_protection(commits)
    axiom_compliance = calc_axiom_compliance(repo)
    
    # Weight components
    weights = {
        'contribution_distribution': 0.25,
        'collaboration_patterns': 0.20,
        'knowledge_sharing': 0.20,
        'flow_state_protection': 0.20,
        'axiom_compliance': 0.15
    }
    
    # Calculate weighted overall score
    overall_score = (
        contribution_distribution['score'] * weights['contribution_distribution'] +
        collaboration_patterns['score'] * weights['collaboration_patterns'] +
        knowledge_sharing['score'] * weights['knowledge_sharing'] +
        flow_state_protection['score'] * weights['flow_state_protection'] +
        axiom_compliance['score'] * weights['axiom_compliance']
    )
    
    # Determine health status
    if overall_score >= 85:
        health_status = "THRIVING"
        status_emoji = "🟢"
    elif overall_score >= 70:
        health_status = "STABLE"
        status_emoji = "🟡"
    elif overall_score >= 50:
        health_status = "STRESSED"
        status_emoji = "🟠"
    else:
        health_status = "CRITICAL"
        status_emoji = "🔴"
    
    return {
        "@context": "https://lvarian.org/metrics/v1",
        "@type": "LatticeHealthAssessment",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "repository": repo_name,
        "assessment_period_days": 90,
        "overall_health_score": round(overall_score, 2),
        "health_status": health_status,
        "status_emoji": status_emoji,
        "components": {
            "contribution_distribution": contribution_distribution,
            "collaboration_patterns": collaboration_patterns,
            "knowledge_sharing": knowledge_sharing,
            "flow_state_protection": flow_state_protection,
            "axiom_compliance": axiom_compliance
        },
        "weights": weights,
        "recommendations": generate_recommendations(
            contribution_distribution,
            collaboration_patterns,
            knowledge_sharing,
            flow_state_protection,
            axiom_compliance
        )
    }


def calc_contribution_distribution(commits: List) -> dict:
    """Calculate how evenly contributions are distributed."""
    if not commits:
        return {"score": 0, "details": "No commits found"}
    
    # Count commits per author
    author_commits = {}
    for commit in commits:
        if commit.author:
            author = commit.author.login
            author_commits[author] = author_commits.get(author, 0) + 1
    
    if not author_commits:
        return {"score": 0, "details": "No authored commits found"}
    
    total_commits = sum(author_commits.values())
    num_contributors = len(author_commits)
    
    # Calculate Gini coefficient (lower = more equal)
    sorted_commits = sorted(author_commits.values())
    cumulative = 0
    for i, commits_count in enumerate(sorted_commits):
        cumulative += (2 * (i + 1) - num_contributors - 1) * commits_count
    
    gini = cumulative / (num_contributors * total_commits) if total_commits > 0 else 0
    
    # Convert to score (lower gini = higher score)
    # Perfect equality (gini=0) = 100, maximum inequality (gini=1) = 0
    score = max(0, min(100, (1 - gini) * 100))
    
    # Check for bus factor risk
    top_contributor_pct = max(author_commits.values()) / total_commits * 100
    bus_factor_risk = "HIGH" if top_contributor_pct > 50 else "MEDIUM" if top_contributor_pct > 30 else "LOW"
    
    return {
        "score": round(score, 2),
        "total_contributors": num_contributors,
        "total_commits": total_commits,
        "gini_coefficient": round(gini, 4),
        "top_contributor_percentage": round(top_contributor_pct, 2),
        "bus_factor_risk": bus_factor_risk,
        "details": f"{num_contributors} contributors, Gini={gini:.3f}"
    }


def calc_collaboration_patterns(pulls: List) -> dict:
    """Analyze collaboration patterns in PRs."""
    if not pulls:
        return {"score": 50, "details": "No PRs found"}
    
    reviewed_pulls = 0
    multi_reviewer_pulls = 0
    cross_team_reviews = 0  # Simplified: different orgs
    
    for pr in pulls:
        if pr.merged_at or pr.state == 'closed':
            try:
                reviews = list(pr.get_reviews())
                if reviews:
                    reviewed_pulls += 1
                    unique_reviewers = set(r.user.login for r in reviews if r.user)
                    if len(unique_reviewers) > 1:
                        multi_reviewer_pulls += 1
            except:
                pass
    
    review_rate = reviewed_pulls / len(pulls) * 100 if pulls else 0
    multi_reviewer_rate = multi_reviewer_pulls / reviewed_pulls * 100 if reviewed_pulls > 0 else 0
    
    # Score based on review culture
    score = (review_rate * 0.6 + multi_reviewer_rate * 0.4)
    
    return {
        "score": round(min(100, score), 2),
        "total_prs": len(pulls),
        "reviewed_prs": reviewed_pulls,
        "multi_reviewer_prs": multi_reviewer_pulls,
        "review_rate": round(review_rate, 2),
        "multi_reviewer_rate": round(multi_reviewer_rate, 2),
        "details": f"{review_rate:.1f}% PRs reviewed, {multi_reviewer_rate:.1f}% with multiple reviewers"
    }


def calc_knowledge_sharing(commits: List, issues: List) -> dict:
    """Evaluate knowledge sharing through docs and discussions."""
    if not commits and not issues:
        return {"score": 50, "details": "No activity found"}
    
    # Look for documentation commits
    doc_commits = sum(1 for c in commits if any(
        kw in c.commit.message.lower() 
        for kw in ['doc', 'readme', 'guide', 'tutorial', 'wiki']
    ))
    
    # Look for well-commented code (simplified: check commit message length)
    detailed_messages = sum(1 for c in commits if len(c.commit.message) > 100)
    
    # Issue discussion quality
    issue_comments = sum(issue.comments for issue in issues if hasattr(issue, 'comments'))
    avg_comments_per_issue = issue_comments / len(issues) if issues else 0
    
    # Calculate score
    doc_ratio = doc_commits / len(commits) * 100 if commits else 0
    detail_ratio = detailed_messages / len(commits) * 100 if commits else 0
    
    score = min(100, (doc_ratio * 0.4 + detail_ratio * 0.3 + min(avg_comments_per_issue * 10, 30)))
    
    return {
        "score": round(score, 2),
        "documentation_commits": doc_commits,
        "detailed_commit_messages": detailed_messages,
        "total_issue_comments": issue_comments,
        "avg_comments_per_issue": round(avg_comments_per_issue, 2),
        "details": f"Docs: {doc_ratio:.1f}%, Detailed messages: {detail_ratio:.1f}%"
    }


def calc_flow_state_protection(commits: List) -> dict:
    """Assess whether contributors have uninterrupted flow time."""
    if not commits:
        return {"score": 50, "details": "No commits found"}
    
    # Analyze commit timing patterns
    # Good flow state = commits clustered in work sessions, not scattered
    
    author_sessions = {}
    for commit in commits:
        if commit.author:
            author = commit.author.login
            if author not in author_sessions:
                author_sessions[author] = []
            author_sessions[author].append(commit.commit.author.date)
    
    # Calculate average session coherence (simplified)
    coherence_scores = []
    for author, dates in author_sessions.items():
        if len(dates) < 2:
            continue
        dates.sort()
        # Check if commits are in reasonable clusters (not every minute, not every week)
        gaps = [(dates[i+1] - dates[i]).total_seconds() / 3600 for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 24
        
        # Optimal gap is 1-8 hours (good flow without burnout)
        if 1 <= avg_gap <= 8:
            coherence_scores.append(100)
        elif avg_gap < 1:
            coherence_scores.append(max(50, 100 - avg_gap * 50))  # Too frequent
        else:
            coherence_scores.append(max(50, 100 - (avg_gap - 8) * 5))  # Too spread out
    
    avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 50
    
    return {
        "score": round(min(100, max(0, avg_coherence)), 2),
        "active_authors": len(author_sessions),
        "average_hourly_gap": round(sum(gaps) / len(gaps), 2) if gaps else 0,
        "details": f"Flow coherence: {avg_coherence:.1f}%"
    }


def calc_axiom_compliance(repo) -> dict:
    """Check basic axiom compliance indicators."""
    score = 100
    issues = []
    
    # Check for Code of Conduct (E₁ - equity)
    try:
        repo.get_contents("CODE_OF_CONDUCT.md")
    except:
        score -= 15
        issues.append("Missing CODE_OF_CONDUCT.md")
    
    # Check for CONTRIBUTING guide (E₁ - equal access)
    try:
        repo.get_contents("CONTRIBUTING.md")
    except:
        score -= 10
        issues.append("Missing CONTRIBUTING.md")
    
    # Check for LICENSE (N₁/E₁ - clear rights)
    try:
        repo.get_contents("LICENSE") or repo.get_contents("LICENSE.md") or repo.get_contents("LICENSE.MD")
    except:
        score -= 15
        issues.append("Missing LICENSE file")
    
    # Check for inclusive language (simplified)
    try:
        readme = repo.get_contents("README.md").decoded_content.decode()
        problematic_terms = ['master', 'slave', 'blacklist', 'whitelist']
        found_terms = [t for t in problematic_terms if t.lower() in readme.lower()]
        if found_terms:
            score -= 10
            issues.append(f"Potentially non-inclusive terms: {found_terms}")
    except:
        pass
    
    return {
        "score": max(0, score),
        "compliance_issues": issues,
        "details": f"Score: {score}/100" + (f", Issues: {len(issues)}" if issues else "")
    }


def generate_recommendations(*components) -> List[str]:
    """Generate actionable recommendations based on component scores."""
    recommendations = []
    
    for component in components:
        score = component.get('score', 50)
        
        if score < 50:
            if 'gini_coefficient' in component:
                recommendations.append("🎯 Diversify contributions: Encourage broader participation to reduce bus factor risk")
            elif 'review_rate' in component:
                recommendations.append("📝 Strengthen code review culture: Require reviews before merging")
            elif 'documentation_commits' in component:
                recommendations.append("📚 Invest in documentation: Allocate time for knowledge sharing")
            elif 'coherence' in str(component):
                recommendations.append("🧘 Protect flow states: Reduce meeting fragmentation, enable deep work blocks")
            elif 'compliance_issues' in component:
                recommendations.append("⚖️ Address axiom compliance: Add missing governance documents")
    
    return recommendations[:5]  # Top 5 recommendations


def main():
    parser = argparse.ArgumentParser(description="Assess lattice health")
    parser.add_argument("--repo", type=str, required=True, help="Repository name")
    parser.add_argument("--token", type=str, required=True, help="GitHub API token")
    parser.add_argument("--tau-metrics", type=str, help="Path to τ-metrics JSON")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"🕸️ Assessing lattice health for {args.repo}...")
    
    tau_metrics = None
    if args.tau_metrics:
        try:
            with open(args.tau_metrics) as f:
                tau_metrics = json.load(f)
            print(f"   Loaded τ-metrics from {args.tau_metrics}")
        except Exception as e:
            print(f"   Warning: Could not load τ-metrics: {e}")
    
    try:
        health = assess_lattice_health(args.repo, args.token, tau_metrics)
        
        print(f"\n## Lattice Health Assessment")
        print(f"   Overall Score: {health['overall_health_score']}/100")
        print(f"   Status: {health['status_emoji']} {health['health_status']}")
        print(f"\n### Component Scores")
        for name, data in health['components'].items():
            print(f"   - {name.replace('_', ' ').title()}: {data['score']}/100")
        
        if health['recommendations']:
            print(f"\n### Recommendations")
            for rec in health['recommendations']:
                print(f"   {rec}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(health, f, indent=2)
            print(f"\n💾 Health assessment saved to: {args.output}")
        else:
            print("\n\nFull JSON:")
            print(json.dumps(health, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error assessing lattice health: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
