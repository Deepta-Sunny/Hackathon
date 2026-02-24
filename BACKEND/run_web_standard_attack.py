"""
Run Standard Attack against Web-Based Chatbot (Tia - Air India Express)
Uses ThreeRunCrescendoOrchestrator with execute_full_assessment() for standard attack mode
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import ThreeRunCrescendoOrchestrator
from core.web_screen_target import WebScreenTarget
from models.chatbot_profile import ChatbotProfile


async def main():
    print("="*80)
    print("🎯 STANDARD RED TEAM ATTACK - Web Chatbot (Tia)")
    print("="*80)
    print(f"Target: Air India Express - Tia Chatbot")
    print(f"Attack Mode: Standard (3 runs, adaptive)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Configuration
    target_url = "https://www.airindiaexpress.com/"
    headless = False  # Set to True for production
    
    # Create chatbot profile for Aviation/Airline domain
    chatbot_profile = ChatbotProfile(
        username="RedTeamTester",
        websocket_url="ws://web-interface",  # Placeholder for web-based target
        domain="Aviation/Airline Customer Service",
        primary_objective="Assist customers with flight bookings, cancellations, refunds, check-in, flight status, and general inquiries",
        intended_audience="Air India Express customers and potential passengers",
        chatbot_role="Helpful virtual assistant (Tia) for airline customer service",
        capabilities=[
            "Flight booking information",
            "Cancellation and refund processing",
            "Flight status updates",
            "Web check-in assistance",
            "Booking modifications",
            "Customer complaints and appreciation",
            "General airline policies"
        ],
        boundaries="Must maintain customer privacy and data security. Should not share other passengers' information. Must follow airline regulatory compliance. Should not process unauthorized transactions. Must verify identity before sharing booking details. Should not make unauthorized flight changes. Must adhere to terms and conditions of carriage.",
        communication_style="Friendly, professional, and helpful. Uses emojis for warmth. Clear and concise responses."
    )
    
    print(f"📋 Chatbot Profile Created:")
    print(f"   Domain: {chatbot_profile.domain}")
    print(f"   Primary Objective: {chatbot_profile.primary_objective}")
    print(f"   Role: {chatbot_profile.chatbot_role}")
    print(f"   Capabilities: {len(chatbot_profile.capabilities)} defined")
    print(f"   Boundaries: {chatbot_profile.boundaries[:100]}...\n")
    
    # Initialize Web Target
    print("🌐 Initializing Web Screen Target...")
    web_target = WebScreenTarget(
        url=target_url,
        headless=headless
    )
    
    try:
        # Connect to target
        print("🔗 Connecting to Air India Express chatbot...")
        await web_target.connect()
        print("✅ Connected successfully!\n")
        
        # Initialize orchestrator for STANDARD attack (execute_full_assessment)
        print("🎭 Initializing Standard Attack Orchestrator...")
        orchestrator = ThreeRunCrescendoOrchestrator(
            websocket_url=None,  # Not using websocket
            architecture_file=None,  # Using chatbot_profile instead
            chatbot_profile=chatbot_profile
        )
        
        # Replace the chatbot target with our web target
        orchestrator.chatbot_target = web_target
        
        print("✅ Orchestrator ready\n")
        
        # Execute standard attack
        print("🚀 Starting Standard Attack Assessment...")
        print("-"*80)
        final_report = await orchestrator.execute_full_assessment()
        print("-"*80)
        print("✅ Standard Attack Complete!\n")
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"tia_standard_attack_{timestamp}.json"
        report_path = Path(__file__).parent / "attack_results" / report_filename
        
        # Ensure directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        print(f"💾 Saving report to: {report_filename}")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print("✅ Report saved successfully!\n")
        
        # Display summary
        print("="*80)
        print("📊 ATTACK SUMMARY")
        print("="*80)
        print(f"Total Vulnerabilities: {final_report.get('total_vulnerabilities', 0)}")
        print(f"Risk Score: {final_report.get('total_risk_score', 0)}")
        
        severity_counts = final_report.get('severity_counts', {})
        print(f"\nBy Severity:")
        print(f"   🔴 CRITICAL: {severity_counts.get('CRITICAL', 0)}")
        print(f"   🟠 HIGH:     {severity_counts.get('HIGH', 0)}")
        print(f"   🟡 MEDIUM:   {severity_counts.get('MEDIUM', 0)}")
        print(f"   🔵 LOW:      {severity_counts.get('LOW', 0)}")
        
        print(f"\nReport saved to: {report_path}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during attack execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await web_target.disconnect()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())