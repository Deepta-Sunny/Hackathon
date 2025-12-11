"""
Test script to verify Skeleton Key Attack implementation.
Checks imports, class structure, and method availability.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import WEBSOCKET_URL

def test_skeleton_key_import():
    """Test that SkeletonKeyAttackOrchestrator can be imported."""
    try:
        from core.skeleton_key_orchestrator import (
            SkeletonKeyAttackOrchestrator,
            SkeletonKeyPromptTransformer
        )
        print("✅ Successfully imported SkeletonKeyAttackOrchestrator")
        print("✅ Successfully imported SkeletonKeyPromptTransformer")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_skeleton_key_structure():
    """Test the structure of SkeletonKeyAttackOrchestrator."""
    try:
        from core.skeleton_key_orchestrator import (
            SkeletonKeyAttackOrchestrator,
            SkeletonKeyPromptTransformer
        )
        
        # Check SkeletonKeyPromptTransformer methods
        transformer_methods = [
            'transform_seed_prompts',
            '_load_skeleton_key_history',
            '_build_findings_context',
            '_parse_json_response',
            '_generate_fallback_skeleton_key'
        ]
        
        for method in transformer_methods:
            if hasattr(SkeletonKeyPromptTransformer, method):
                print(f"✅ SkeletonKeyPromptTransformer.{method} exists")
            else:
                print(f"❌ SkeletonKeyPromptTransformer.{method} missing")
                return False
        
        # Check SkeletonKeyAttackOrchestrator methods
        orchestrator_methods = [
            'execute_skeleton_key_assessment',
            '_build_chatbot_profile',
            '_execute_skeleton_key_run',
            '_analyze_skeleton_key_response',
            '_fallback_skeleton_key_analysis',
            '_generate_skeleton_key_report',
            '_generalize_skeleton_key_patterns'
        ]
        
        for method in orchestrator_methods:
            if hasattr(SkeletonKeyAttackOrchestrator, method):
                print(f"✅ SkeletonKeyAttackOrchestrator.{method} exists")
            else:
                print(f"❌ SkeletonKeyAttackOrchestrator.{method} missing")
                return False
        
        # Check default seed prompts
        if hasattr(SkeletonKeyPromptTransformer, 'DEFAULT_SKELETON_KEY_SEEDS'):
            seeds = SkeletonKeyPromptTransformer.DEFAULT_SKELETON_KEY_SEEDS
            print(f"✅ DEFAULT_SKELETON_KEY_SEEDS exists ({len(seeds)} seeds)")
            if len(seeds) >= 10:
                print(f"✅ Sufficient default seeds (10+)")
            else:
                print(f"⚠️  Only {len(seeds)} default seeds (expected 10+)")
        else:
            print("❌ DEFAULT_SKELETON_KEY_SEEDS missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

def test_config_settings():
    """Test that config settings include Skeleton Key parameters."""
    try:
        from config.settings import SKELETON_KEY_RUNS, SKELETON_KEY_TURNS_PER_RUN
        
        print(f"✅ SKELETON_KEY_RUNS = {SKELETON_KEY_RUNS}")
        print(f"✅ SKELETON_KEY_TURNS_PER_RUN = {SKELETON_KEY_TURNS_PER_RUN}")
        
        # Validate values
        if SKELETON_KEY_RUNS == 3:
            print("✅ SKELETON_KEY_RUNS correctly set to 3")
        else:
            print(f"⚠️  SKELETON_KEY_RUNS is {SKELETON_KEY_RUNS} (expected 3)")
        
        if SKELETON_KEY_TURNS_PER_RUN == 10:
            print("✅ SKELETON_KEY_TURNS_PER_RUN correctly set to 10")
        else:
            print(f"⚠️  SKELETON_KEY_TURNS_PER_RUN is {SKELETON_KEY_TURNS_PER_RUN} (expected 10)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_main_integration():
    """Test that main.py includes Skeleton Key option."""
    try:
        main_file = Path(__file__).parent / "main.py"
        
        if not main_file.exists():
            print("❌ main.py not found")
            return False
        
        content = main_file.read_text()
        
        # Check for Skeleton Key import
        if "from core.skeleton_key_orchestrator import SkeletonKeyAttackOrchestrator" in content:
            print("✅ main.py imports SkeletonKeyAttackOrchestrator")
        else:
            print("❌ main.py missing Skeleton Key import")
            return False
        
        # Check for option 3 menu
        if "3. Skeleton Key Attack" in content:
            print("✅ main.py includes Skeleton Key menu option")
        else:
            print("❌ main.py missing Skeleton Key menu option")
            return False
        
        # Check for attack_mode == "skeleton_key"
        if 'attack_mode == "skeleton_key"' in content:
            print("✅ main.py includes Skeleton Key mode routing")
        else:
            print("❌ main.py missing Skeleton Key mode routing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Main integration test failed: {e}")
        return False

def test_instantiation():
    """Test that SkeletonKeyAttackOrchestrator can be instantiated."""
    try:
        from core.skeleton_key_orchestrator import SkeletonKeyAttackOrchestrator
        
        orchestrator = SkeletonKeyAttackOrchestrator(
            websocket_url=WEBSOCKET_URL,
            architecture_file="docs/MD.txt",
            total_runs=3,
            turns_per_run=10
        )
        
        print("✅ SkeletonKeyAttackOrchestrator instantiated successfully")
        
        # Check attributes
        if orchestrator.websocket_url == WEBSOCKET_URL:
            print("✅ websocket_url set correctly")
        else:
            print(f"⚠️  websocket_url = {orchestrator.websocket_url}")
        
        if orchestrator.total_runs == 3:
            print("✅ total_runs set correctly")
        else:
            print(f"⚠️  total_runs = {orchestrator.total_runs}")
        
        if orchestrator.turns_per_run == 10:
            print("✅ turns_per_run set correctly")
        else:
            print(f"⚠️  turns_per_run = {orchestrator.turns_per_run}")
        
        # Check components initialized
        if hasattr(orchestrator, 'azure_client'):
            print("✅ azure_client initialized")
        else:
            print("❌ azure_client not initialized")
            return False
        
        if hasattr(orchestrator, 'prompt_transformer'):
            print("✅ prompt_transformer initialized")
        else:
            print("❌ prompt_transformer not initialized")
            return False
        
        if hasattr(orchestrator, 'vulnerable_memory'):
            print("✅ vulnerable_memory initialized")
        else:
            print("❌ vulnerable_memory not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Instantiation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("SKELETON KEY ATTACK - VERIFICATION TESTS")
    print("="*70)
    
    tests = [
        ("Import Test", test_skeleton_key_import),
        ("Structure Test", test_skeleton_key_structure),
        ("Config Test", test_config_settings),
        ("Main Integration Test", test_main_integration),
        ("Instantiation Test", test_instantiation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 All tests passed! Skeleton Key Attack is ready to use.")
        print("\nRun: python main.py")
        print("Select: 3 (Skeleton Key Attack)")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
