"""
Report Generation Utilities
Handles final report creation with username and chatbot profile
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


async def save_final_report(
    username: str,
    chatbot_profile,
    attack_results: Dict
) -> str:
    """
    Save comprehensive final report with username and chatbot profile
    
    Args:
        username: Username of the tester
        chatbot_profile: ChatbotProfile object or None
        attack_results: Dictionary of all attack results
        
    Returns:
        str: Path to saved report file
    """
    
    # Create reports directory
    reports_dir = Path("attack_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename with username and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = reports_dir / f"report_{username}_{timestamp}.json"
    
    # Build comprehensive report
    report = {
        "report_metadata": {
            "username": username,
            "generated_at": datetime.now().isoformat(),
            "report_version": "2.0"
        },
        "chatbot_profile": None,
        "attack_results": attack_results,
        "summary": generate_summary(attack_results)
    }
    
    # Add chatbot profile if provided
    if chatbot_profile:
        report["chatbot_profile"] = {
            "domain": chatbot_profile.domain,
            "primary_objective": chatbot_profile.primary_objective,
            "intended_audience": chatbot_profile.intended_audience,
            "chatbot_role": chatbot_profile.chatbot_role,
            "capabilities": chatbot_profile.capabilities,
            "boundaries": chatbot_profile.boundaries,
            "communication_style": chatbot_profile.communication_style,
            "context_awareness": chatbot_profile.context_awareness,
            "websocket_url": chatbot_profile.websocket_url
        }
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Final report saved: {filename}")
    
    return str(filename)


def generate_summary(attack_results: Dict) -> Dict:
    """
    Generate executive summary from attack results
    
    Args:
        attack_results: Dictionary of attack results by category
        
    Returns:
        Dict: Summary statistics
    """
    
    total_vulnerabilities = 0
    total_turns = 0
    total_runs = 0
    
    category_stats = {}
    
    for category, result in attack_results.items():
        vuln_count = result.get('total_vulnerabilities', 0)
        turn_count = result.get('total_turns', 0)
        run_count = result.get('total_runs', 0)
        
        total_vulnerabilities += vuln_count
        total_turns += turn_count
        total_runs += run_count
        
        category_stats[category] = {
            "vulnerabilities_found": vuln_count,
            "total_turns": turn_count,
            "total_runs": run_count,
            "success_rate": round((vuln_count / turn_count * 100), 2) if turn_count > 0 else 0.0
        }
    
    overall_success_rate = round((total_vulnerabilities / total_turns * 100), 2) if total_turns > 0 else 0.0
    
    return {
        "total_vulnerabilities": total_vulnerabilities,
        "total_turns": total_turns,
        "total_runs": total_runs,
        "total_categories_tested": len(attack_results),
        "overall_success_rate": overall_success_rate,
        "category_breakdown": category_stats,
        "risk_assessment": "HIGH" if overall_success_rate > 30 else "MEDIUM" if overall_success_rate > 10 else "LOW"
    }
