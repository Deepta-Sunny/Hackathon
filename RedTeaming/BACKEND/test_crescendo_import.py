"""Quick test to verify Crescendo imports work correctly."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from config.settings import CRESCENDO_RUNS, CRESCENDO_TURNS_PER_RUN, CRESCENDO_RECON_TURNS
    print(f"✅ Config: CRESCENDO_RUNS={CRESCENDO_RUNS}, TURNS={CRESCENDO_TURNS_PER_RUN}, RECON={CRESCENDO_RECON_TURNS}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

try:
    from core.crescendo_orchestrator import CrescendoAttackOrchestrator, CrescendoPersonality, CrescendoPromptGenerator
    print(f"✅ Crescendo classes imported successfully")
    print(f"   - CrescendoAttackOrchestrator: {CrescendoAttackOrchestrator.__name__}")
    print(f"   - CrescendoPersonality: {CrescendoPersonality.__name__}")
    print(f"   - CrescendoPromptGenerator: {CrescendoPromptGenerator.__name__}")
except Exception as e:
    print(f"❌ Crescendo import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    # Test personality detection
    test_arch = "This is an ecommerce system with product catalog and shopping cart"
    domain = CrescendoPersonality.detect_domain(test_arch)
    personality = CrescendoPersonality.get_personality(domain)
    print(f"\n✅ Domain detection works:")
    print(f"   - Detected domain: {domain}")
    print(f"   - Personality: {personality['name']}")
    print(f"   - Backstory preview: {personality['backstory'][:80]}...")
    print(f"   - Target behaviors: {len(personality['target_behaviors'])} items")
except Exception as e:
    print(f"❌ Personality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports and basic functionality verified!")
print("\nAvailable personalities:")
for domain, persona in CrescendoPersonality.PERSONALITIES.items():
    print(f"   • {domain}: {persona['name']}")
