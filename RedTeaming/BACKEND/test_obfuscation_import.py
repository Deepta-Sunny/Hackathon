"""
Test script to verify Obfuscation Attack implementation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import WEBSOCKET_URL


def test_obfuscation_imports():
    """Test that obfuscation classes can be imported."""
    try:
        from attack_strategies.obfuscation import (
            ObfuscationAttacks,
            SemanticObfuscationAttacks,
            LinguisticObfuscationAttacks,
            ContextualObfuscationAttacks,
            TokenObfuscationAttacks,
            ChainedObfuscationAttacks
        )
        print("✅ All obfuscation strategy classes imported successfully")
        
        from core.obfuscation_orchestrator import (
            ObfuscationAttackOrchestrator,
            ObfuscationPromptGenerator
        )
        print("✅ Obfuscation orchestrator classes imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_obfuscation_strategies():
    """Test obfuscation strategy initialization."""
    try:
        from attack_strategies.obfuscation import (
            ObfuscationAttacks,
            SemanticObfuscationAttacks,
            LinguisticObfuscationAttacks
        )
        
        strategies = [
            ObfuscationAttacks(),
            SemanticObfuscationAttacks(),
            LinguisticObfuscationAttacks()
        ]
        
        for strategy in strategies:
            prompts = strategy.get_prompts()
            if len(prompts) > 0:
                print(f"✅ {strategy.technique_name}: {len(prompts)} prompts")
            else:
                print(f"❌ {strategy.technique_name}: No prompts generated")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False


def test_orchestrator_instantiation():
    """Test ObfuscationAttackOrchestrator instantiation."""
    try:
        from core.obfuscation_orchestrator import ObfuscationAttackOrchestrator
        
        orchestrator = ObfuscationAttackOrchestrator(
            websocket_url=WEBSOCKET_URL,
            architecture_file="docs/MD.txt",
            total_runs=3,
            turns_per_run=20
        )
        
        print("✅ ObfuscationAttackOrchestrator instantiated")
        print(f"   • WebSocket URL: {orchestrator.websocket_url}")
        print(f"   • Total runs: {orchestrator.total_runs}")
        print(f"   • Turns per run: {orchestrator.turns_per_run}")
        
        # Check components
        if hasattr(orchestrator, 'azure_client'):
            print("✅ Azure client initialized")
        else:
            print("❌ Azure client not initialized")
            return False
        
        if hasattr(orchestrator, 'prompt_generator'):
            print("✅ Prompt generator initialized")
        else:
            print("❌ Prompt generator not initialized")
            return False
        
        if hasattr(orchestrator, 'vulnerable_memory'):
            print("✅ Vulnerable memory initialized")
        else:
            print("❌ Vulnerable memory not initialized")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_attack_strategy_orchestrator():
    """Test that attack strategy orchestrator includes obfuscation."""
    try:
        from attack_strategies.orchestrator import AttackStrategyOrchestrator
        
        orchestrator = AttackStrategyOrchestrator(use_safe_mode=False)
        
        if "obfuscation" in orchestrator.strategies:
            print("✅ Obfuscation strategies registered in orchestrator")
            obfuscation = orchestrator.strategies["obfuscation"]
            if isinstance(obfuscation, list):
                print(f"   • {len(obfuscation)} obfuscation sub-strategies")
            else:
                print(f"   • Single obfuscation strategy: {obfuscation.technique_name}")
            return True
        else:
            print("❌ Obfuscation not found in orchestrator strategies")
            print(f"   Available strategies: {list(orchestrator.strategies.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Strategy orchestrator test failed: {e}")
        return False


def test_config():
    """Test obfuscation configuration."""
    try:
        from config.settings import OBFUSCATION_RUNS, OBFUSCATION_TURNS_PER_RUN
        
        print(f"✅ OBFUSCATION_RUNS = {OBFUSCATION_RUNS}")
        print(f"✅ OBFUSCATION_TURNS_PER_RUN = {OBFUSCATION_TURNS_PER_RUN}")
        
        if OBFUSCATION_RUNS == 3 and OBFUSCATION_TURNS_PER_RUN == 20:
            print("✅ Configuration values correct")
            return True
        else:
            print("⚠️  Configuration values differ from defaults")
            return True  # Not a failure
            
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("OBFUSCATION ATTACK - VERIFICATION TESTS")
    print("="*70)
    
    tests = [
        ("Import Test", test_obfuscation_imports),
        ("Strategy Test", test_obfuscation_strategies),
        ("Config Test", test_config),
        ("Orchestrator Instantiation Test", test_orchestrator_instantiation),
        ("Attack Strategy Orchestrator Test", test_attack_strategy_orchestrator),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print("="*70)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
