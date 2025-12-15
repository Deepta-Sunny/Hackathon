"""
Fetch and display vulnerable prompts using O(1) retrieval
"""

from core.memory_manager import DuckDBMemoryManager

def main():
    print("=" * 80)
    print("Fetching Vulnerable Prompts - O(1) Retrieval")
    print("=" * 80)
    
    # Initialize DB manager
    db = DuckDBMemoryManager()
    
    # O(1) retrieval - Direct access by run/turn
    print("\n1. O(1) Retrieval - Get specific prompt (run=2, turn=10):")
    print("-" * 80)
    prompt = db.get_vulnerable_prompt(run=2, turn=10)
    if prompt:
        print(f"Key: run2_turn10")
        print(f"Risk: {prompt['risk_label']} ({prompt['risk_level']})")
        print(f"Attack Category: {prompt['attack_category']}")
        print(f"\nPrompt:\n{prompt['prompt']}")
        print(f"\nAbstract:\n{prompt['abstract']}")
        print(f"\nResponse Preview:\n{prompt['response_preview']}")
    else:
        print("❌ Prompt not found")
    
    # Filter by risk level
    print("\n\n2. Filter by Risk Level - HIGH (4):")
    print("-" * 80)
    high_risk = db.get_prompts_by_risk_level(4)
    print(f"Found {len(high_risk)} HIGH risk prompts:")
    for prompt in high_risk:
        print(f"  • Run {prompt['run']}, Turn {prompt['turn']}: {prompt['prompt'][:60]}...")
    
    # Filter by category
    print("\n\n3. Filter by Category - unauthorized_claims:")
    print("-" * 80)
    unauthorized = db.get_prompts_by_category("unauthorized_claims")
    print(f"Found {len(unauthorized)} unauthorized_claims prompts:")
    for prompt in unauthorized:
        print(f"  • Run {prompt['run']}, Turn {prompt['turn']}: {prompt['prompt'][:60]}...")
    
    # Get all prompts
    print("\n\n4. All Vulnerable Prompts Summary:")
    print("-" * 80)
    all_prompts = db.get_all_vulnerable_prompts()
    print(f"Total prompts stored: {len(all_prompts)}\n")
    
    for key, prompt in all_prompts.items():
        print(f"[{key}]")
        print(f"  Risk: {prompt['risk_label']} ({prompt['risk_level']})")
        print(f"  Category: {prompt['attack_category']}")
        print(f"  Prompt: {prompt['prompt'][:60]}...")
        print(f"  Abstract: {prompt['abstract'][:100]}...")
        print()
    
    print("=" * 80)
    print("✅ Fetch Complete!")
    print("=" * 80)
    
    # Clean up
    db.close()


if __name__ == "__main__":
    main()
