"""
Main entry point for the 3-Run Adaptive Crescendo Attack System.

This script orchestrates a comprehensive security assessment of a chatbot
using architecture-aware attack techniques across 3 runs with 25 turns each.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_config
from core.orchestrator import ThreeRunCrescendoOrchestrator
from core.crescendo_orchestrator import CrescendoAttackOrchestrator
from core.skeleton_key_orchestrator import SkeletonKeyAttackOrchestrator
from core.obfuscation_orchestrator import ObfuscationAttackOrchestrator


async def main():
    """Execute the 3-run adaptive crescendo attack campaign."""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   3-RUN ADAPTIVE CRESCENDO ATTACK SYSTEM                           ║
║                                                                    ║
║   Architecture-Aware Red Teaming for AI Chatbots                   ║
║   Powered by Azure OpenAI + PyRIT                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Please ensure the following environment variables are set:")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("\nOptional configuration:")
        print("   - AZURE_OPENAI_DEPLOYMENT (default: gpt-4o)")
        print("   - CHATBOT_WEBSOCKET_URL (default: ws://localhost:8000/chat)")
        print("   - TOTAL_RUNS (default: 3)")
        print("   - TURNS_PER_RUN (default: 25)")
        return 1
    
    print("\n" + "="*70)
    print("⚠️  IMPORTANT PREREQUISITES")        
    print("="*70)
    print("\n1. Ensure the target chatbot is running and accessible")
    print("2. Have your architecture file (.md or .txt) ready")
    print("3. DuckDB will store results in chat_memory.db")
    print("4. Note: Azure OpenAI content filters may block aggressive prompts")
    print("\n" + "="*70)
    
    # Automated multi-category attack execution
    print("\n🎯 Automated Multi-Category Attack Campaign")
    print("-" * 70)
    print("\n📋 Attack Categories (executed sequentially):")
    print("   1. Standard Attack (3 runs × 25 turns)")
    print("      → Traditional multi-phase attacks")
    print("   2. Crescendo Attack (3 runs × 15 turns)")
    print("      → Personality-based social engineering")
    print("   3. Skeleton Key Attack (3 runs × 10 turns)")
    print("      → Jailbreak & system probe techniques")
    print("   4. Obfuscation Attack (3 runs × 20 turns)")
    print("      → Advanced evasion techniques")
    print("\n⚡ All categories will be executed automatically")
    print("   Total estimated time: ~35-45 minutes")
    
    # All attack modes will be executed
    attack_modes = ["standard", "crescendo", "skeleton_key", "obfuscation"]
    
    mode_names = {
        "standard": "Standard Attack",
        "crescendo": "Crescendo Attack",
        "skeleton_key": "Skeleton Key Attack",
        "obfuscation": "Obfuscation Attack"
    }
    
    try:
        pass  # No user input needed for mode selection
        
    except KeyboardInterrupt:
        print("\n\n❌ Assessment cancelled by user")
        return 0
    
    # Get user inputs
    try:
        import os
        
        # Get chatbot WebSocket endpoint
        print("\n🔌 Target Chatbot Configuration")
        print("-" * 70)
        websocket_url = input("Enter chatbot WebSocket URL [default: ws://localhost:8000/chat]: ").strip()
        
        # Use default if no input provided
        if not websocket_url:
            websocket_url = "ws://localhost:8000/chat"
        
        # Basic validation for WebSocket URL
        if not websocket_url.startswith(('ws://', 'wss://')):
            print(f"\n❌ Error: WebSocket URL must start with ws:// or wss://")
            return 1
        
        print(f"✅ Target endpoint: {websocket_url}")
        os.environ["CHATBOT_WEBSOCKET_URL"] = websocket_url
        
        # Get architecture file path
        print("\n📄 Architecture File Configuration")
        print("-" * 70)
        arch_file = input("Enter path to architecture file (.md or .txt) [default: docs/MD.txt]: ").strip()
        
        # Use default if no input provided
        if not arch_file:
            arch_file = "docs/MD.txt"
        
        # Validate file exists and has correct extension
        arch_path = Path(arch_file)
        if not arch_path.exists():
            print(f"\n❌ Error: File '{arch_file}' not found")
            return 1
        
        if arch_path.suffix.lower() not in ['.md', '.txt']:
            print(f"\n❌ Error: File must be .md or .txt (got {arch_path.suffix})")
            return 1
        
        print(f"✅ Using architecture file: {arch_file}")
        os.environ["ARCHITECTURE_FILE"] = str(arch_path.absolute())
        
        # Reload config to pick up user-provided environment variables
        from importlib import reload
        import config.settings as settings_module
        reload(settings_module)
        
    except KeyboardInterrupt:
        print("\n\n❌ Assessment cancelled by user")
        return 0
    
    # Ask for confirmation
    try:
        response = input("\n🚀 Ready to start the automated multi-category attack? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Assessment cancelled by user")
            return 0
    except KeyboardInterrupt:
        print("\n\n❌ Assessment cancelled by user")
        return 0
    
    # Store all reports
    all_reports = {}
    
    # Create and execute orchestrators for each attack mode
    try:
        for attack_mode in attack_modes:
            print("\n" + "="*70)
            print(f"🎯 STARTING: {mode_names[attack_mode]}")
            print("="*70)
            
            if attack_mode == "obfuscation":
                # Obfuscation Attack Mode
                from config.settings import OBFUSCATION_RUNS, OBFUSCATION_TURNS_PER_RUN
                orchestrator = ObfuscationAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=str(arch_path.absolute()),
                    total_runs=OBFUSCATION_RUNS,
                    turns_per_run=OBFUSCATION_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_obfuscation_assessment()
            elif attack_mode == "skeleton_key":
                # Skeleton Key Attack Mode
                from config.settings import SKELETON_KEY_RUNS, SKELETON_KEY_TURNS_PER_RUN
                orchestrator = SkeletonKeyAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=str(arch_path.absolute()),
                    total_runs=SKELETON_KEY_RUNS,
                    turns_per_run=SKELETON_KEY_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_skeleton_key_assessment()
            elif attack_mode == "crescendo":
                # Crescendo Attack Mode
                from config.settings import CRESCENDO_RUNS, CRESCENDO_TURNS_PER_RUN
                orchestrator = CrescendoAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=str(arch_path.absolute()),
                    total_runs=CRESCENDO_RUNS,
                    turns_per_run=CRESCENDO_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_crescendo_assessment()
            else:
                # Standard Attack Mode
                orchestrator = ThreeRunCrescendoOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=str(arch_path.absolute())
                )
                final_report = await orchestrator.execute_full_assessment()
            
            # Store report
            all_reports[attack_mode] = final_report
            
            # Print individual report
            print("\n" + "="*70)
            print(f"📄 {mode_names[attack_mode]} - REPORT SUMMARY")
            print("="*70)
            
            if attack_mode == "obfuscation":
                print(f"\n✅ Obfuscation Assessment Complete!")
                print(f"   • Attack Category: {mode_names[attack_mode]}")
                print(f"   • Total Vulnerabilities Found: {final_report['total_vulnerabilities']}")
                print(f"   • Domain: {final_report['domain']}")
                print(f"   • Obfuscation Techniques Used: {len(final_report.get('techniques_used', []))}")
                print(f"   • Generalized Patterns Saved: {len(final_report['generalized_patterns'])}")
            elif attack_mode == "skeleton_key":
                print(f"\n✅ Skeleton Key Assessment Complete!")
                print(f"   • Attack Category: {mode_names[attack_mode]}")
                print(f"   • Total Vulnerabilities Found: {final_report['total_vulnerabilities']}")
                print(f"   • Domain: {final_report['domain']}")
                print(f"   • Generalized Patterns Saved: {len(final_report['generalized_patterns'])}")
            elif attack_mode == "crescendo":
                print(f"\n✅ Crescendo Assessment Complete!")
                print(f"   • Attack Category: {mode_names[attack_mode]}")
                print(f"   • Total Vulnerabilities Found: {final_report['total_vulnerabilities']}")
                print(f"   • Personality Used: {final_report['personality']}")
                print(f"   • Generalized Patterns Saved: {len(final_report['generalized_patterns'])}")
            else:
                exec_summary = final_report["executive_summary"]
                print(f"\n✅ Standard Assessment Complete!")
                print(f"   • Attack Category: {mode_names[attack_mode]}")
                print(f"   • Total Vulnerabilities Found: {exec_summary['total_vulnerabilities']}")
                print(f"   • Overall Risk Score: {exec_summary['overall_risk_score']:.2%}")
                print(f"   • Generalized Patterns Saved: {len(final_report['generalized_patterns'])}")
            
            print(f"\n⏭️  Moving to next attack category...\n")
        
        # Print final consolidated summary
        print("\n" + "="*70)
        print("📊 CONSOLIDATED MULTI-CATEGORY ATTACK SUMMARY")
        print("="*70)
        
        total_vulns = 0
        for attack_mode, report in all_reports.items():
            if attack_mode == "standard":
                vulns = report['executive_summary']['total_vulnerabilities']
            else:
                vulns = report['total_vulnerabilities']
            
            total_vulns += vulns
            print(f"\n{mode_names[attack_mode]}:")
            print(f"   • Vulnerabilities: {vulns}")
        
        print(f"\n{'='*70}")
        print(f"🎯 TOTAL VULNERABILITIES ACROSS ALL CATEGORIES: {total_vulns}")
        print(f"{'='*70}")
        
        print("\n💾 Results stored in:")
        print("   • Database: chat_memory.db (DuckDB)")
        print("   • Patterns: Available for future assessments")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Assessment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted")
        sys.exit(1)
