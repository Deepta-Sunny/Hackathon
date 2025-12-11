"""
Test script for the Gemini E-Commerce Agent
==========================================

This script provides basic testing functionality for the Gemini agent.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import websockets
except ImportError:
    print("❌ websockets not installed. Install with: pip install websockets")
    sys.exit(1)


async def test_agent_connection():
    """Test basic connection to the Gemini agent."""
    uri = "ws://localhost:8001"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Gemini agent")

            # Test messages
            test_messages = [
                "Hello, I need help with my order",
                "What products do you recommend?",
                "How do I track my shipment?",
                "I want to return an item"
            ]

            for i, message in enumerate(test_messages, 1):
                print(f"\n🧪 Test {i}: Sending '{message}'")

                # Send message
                await websocket.send(json.dumps({"message": message}))

                # Receive response
                response = await websocket.recv()
                data = json.loads(response)

                print(f"🤖 Response: {data.get('response', 'No response')[:100]}...")
                print(f"📊 Conversation length: {data.get('conversation_length', 0)}")

                # Small delay between tests
                await asyncio.sleep(1)

            print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure the Gemini agent is running: python testing/gemini_agent.py")


async def test_memory_persistence():
    """Test that conversation memory persists across messages."""
    uri = "ws://localhost:8001"

    try:
        async with websockets.connect(uri) as websocket:
            print("🧠 Testing memory persistence...")

            # Send a sequence that should show memory
            messages = [
                "My name is John",
                "What's my name?",
                "I like blue shirts",
                "What color shirts do I like?"
            ]

            for message in messages:
                await websocket.send(json.dumps({"message": message}))
                response = await websocket.recv()
                data = json.loads(response)

                print(f"Q: {message}")
                print(f"A: {data.get('response', '')[:80]}...")
                print(f"Memory: {data.get('conversation_length', 0)} messages")
                print("-" * 50)

                await asyncio.sleep(0.5)

            print("✅ Memory test completed!")

    except Exception as e:
        print(f"❌ Memory test failed: {e}")


async def main():
    """Run all tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Gemini E-Commerce Agent")
    parser.add_argument("--test", choices=["connection", "memory", "all"],
                       default="all", help="Which test to run")

    args = parser.parse_args()

    print("🧪 Starting Gemini Agent Tests")
    print("=" * 50)

    if args.test in ["connection", "all"]:
        await test_agent_connection()
        print()

    if args.test in ["memory", "all"]:
        await test_memory_persistence()
        print()

    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())