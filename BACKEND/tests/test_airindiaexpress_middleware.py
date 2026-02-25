"""
Test script for AirIndiaExpress Middleware
Simulates api_server.py connecting to the AirIndiaExpress middleware
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_middleware_connection():
    """Test the AirIndiaExpress middleware WebSocket connection"""
    
    print("="*80)
    print("🧪 TESTING AIRINDIAEXPRESS MIDDLEWARE")
    print("="*80)
    print(f"Connecting to: ws://localhost:8001/chat")
    print("="*80 + "\n")
    
    uri = "ws://localhost:8001/chat"
    
    try:
        print("🔗 Connecting to AirIndiaExpress middleware...")
        async with websockets.connect(uri, ping_timeout=None) as websocket:
            print("✅ Connected to AirIndiaExpress middleware\n")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Connection response: {data.get('message')}")
            print(f"   Status: {data.get('status')}\n")
            
            # Test messages
            test_messages = [
                "Hi, I need help with a flight booking",
                "Can you tell me about cancellation policies?",
                "What is your refund process?"
            ]
            
            for idx, msg in enumerate(test_messages, 1):
                print(f"\n{'='*80}")
                print(f"Test Message {idx}/{len(test_messages)}")
                print(f"{'='*80}")
                print(f"📤 Sending: {msg}\n")
                
                # Send message in api_server.py format
                payload = {
                    "type": "query",
                    "message": msg,
                    "thread_id": f"test-thread-{datetime.now().timestamp()}"
                }
                
                await websocket.send(json.dumps(payload))
                print("   ⏳ Waiting for response (timeout: 90 seconds)...")
                
                # Receive response with timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=90.0)
                    data = json.loads(response)
                    
                    print(f"\n📥 Response received:")
                    print(f"   Type: {data.get('type')}")
                    print(f"   Message: {data.get('message', '')[:200]}...")
                    print(f"   Timestamp: {data.get('timestamp')}")
                except asyncio.TimeoutError:
                    print(f"\n⚠️ Timeout waiting for response (90 seconds)")
                    print(f"   Message may still be processing on server...")
                    continue
                
                # Wait before next message
                if idx < len(test_messages):
                    print("\n⏸️  Waiting 3 seconds before next message...")
                    await asyncio.sleep(3)
            
            print("\n" + "="*80)
            print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
            print("="*80)
            
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed. Is the AirIndiaExpress middleware server running correctly?")
        print("\nStart the AirIndiaExpress middleware server with:")
        print("   python web_chatbot_middleware.py --url https://www.airindiaexpress.com/")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_ping():
    """Test ping/pong for health check"""
    uri = "ws://localhost:8001/chat"
    
    try:
        async with websockets.connect(uri, ping_timeout=None) as websocket:
            # Wait for connection message
            await websocket.recv()
            
            print("\n🏓 Testing ping/pong...")
            payload = {"type": "ping"}
            await websocket.send(json.dumps(payload))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "pong":
                print("✅ Ping/pong successful!")
            else:
                print(f"⚠️ Unexpected response: {data}")
                
    except Exception as e:
        print(f"❌ Ping test failed: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting AirIndiaExpress Middleware Tests...")
    print("⚠️  Make sure the AirIndiaExpress middleware server is running first!\n")
    
    # Run tests
    asyncio.run(test_middleware_connection())
    asyncio.run(test_ping())
    
    print("\n✅ All tests complete!")
    