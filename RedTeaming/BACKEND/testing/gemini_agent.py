"""
Azure OpenAI E-Commerce Assistant Agent for Testing
===================================================

This agent creates a WebSocket-based e-commerce assistant powered by Azure OpenAI.
It maintains conversation history and responds as an e-commerce application assistant.

Features:
- WebSocket communication
- Azure OpenAI integration
- Persistent chat memory
- E-commerce focused responses
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosedError, WebSocketException

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from openai import AzureOpenAI
    from config.settings import (
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_DEPLOYMENT,
        AZURE_OPENAI_API_VERSION
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure openai is installed: pip install openai")
    sys.exit(1)


class AzureEcommerceAgent:
    """
    WebSocket-based Azure OpenAI agent for e-commerce assistance.
    Maintains conversation history and provides intelligent responses.
    """

    def __init__(self, websocket_url: str = "ws://localhost:8000/ws", port: int = 8001):
        """
        Initialize the Azure OpenAI e-commerce agent.

        Args:
            websocket_url: URL of the target WebSocket server to connect to
            port: Port for this agent's WebSocket server
        """
        self.websocket_url = websocket_url
        self.port = port
        self.conversation_history: List[Dict[str, str]] = []
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT

        print("🤖 Azure OpenAI E-Commerce Agent initialized")
        print(f"   📡 Listening on port {self.port}")
        print(f"   🔗 Target WebSocket: {self.websocket_url}")
        print(f"   🔑 Using deployment: {self.deployment}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the e-commerce assistant."""
        return """You are an intelligent assistant for an e-commerce application. Your role is to help customers with:

1. Product recommendations and information
2. Order tracking and status updates
3. Shopping cart management
4. Payment and shipping questions
5. Returns and refunds
6. Account management
7. General customer support

Be helpful, friendly, and professional. Provide accurate information about products, prices, and policies.
If you don't know something specific, admit it and offer to help find the information.

Always maintain context from previous messages in the conversation."""

    def add_to_history(self, role: str, content: str):
        """
        Add a message to the conversation history.

        Args:
            role: 'user' or 'assistant'
            content: The message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": asyncio.get_event_loop().time()
        })

        # Keep only last 50 messages to prevent memory issues
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_recent_history(self, limit: int = 10) -> str:
        """
        Get recent conversation history as formatted text.

        Args:
            limit: Number of recent messages to include

        Returns:
            Formatted conversation history
        """
        recent_messages = self.conversation_history[-limit:]
        history_text = ""

        for msg in recent_messages:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        return history_text.strip()

    async def generate_response(self, user_message: str) -> str:
        """
        Generate a response using Azure OpenAI with conversation context.

        Args:
            user_message: The user's message

        Returns:
            AI-generated response
        """
        try:
            # Rate limiting - wait if needed
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()

            # Add user message to history
            self.add_to_history("user", user_message)

            # Build messages for Azure OpenAI
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-10:]:  # Last 10 messages
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})

            # Generate response
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Extract assistant response
            assistant_response = response.choices[0].message.content.strip()
            self.add_to_history("assistant", assistant_response)

            return assistant_response

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}. How else can I help you?"
            self.add_to_history("assistant", error_msg)
            return error_msg

    async def handle_websocket_connection(self, websocket):
        """
        Handle incoming WebSocket connections and messages.

        Args:
            websocket: The WebSocket connection
        """
        client_address = websocket.remote_address
        print(f"🔗 New connection from {client_address}")

        try:
            async for message in websocket:
                try:
                    # Parse incoming message
                    data = json.loads(message)
                    user_message = data.get('message', '').strip()

                    if not user_message:
                        await websocket.send(json.dumps({
                            "error": "Empty message received"
                        }))
                        continue

                    print(f"📨 Received: {user_message[:100]}...")

                    # Generate response
                    response = await self.generate_response(user_message)

                    # Send only the response text (not wrapped in JSON)
                    await websocket.send(response)
                    print(f"📤 Sent response: ({response})")

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Invalid JSON format"
                    }))
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "error": f"Processing error: {str(e)}"
                    }))

        except ConnectionClosedError:
            print(f"🔌 Connection closed by {client_address}")
        except WebSocketException as e:
            print(f"🔌 WebSocket error from {client_address}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error from {client_address}: {e}")

    async def connect_to_target_websocket(self):
        """
        Connect to the target WebSocket server for testing purposes.
        This allows the agent to interact with other systems.
        """
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                print(f"✅ Connected to target WebSocket: {self.websocket_url}")

                # Send initial greeting
                greeting = {
                    "type": "agent_greeting",
                    "agent": "GeminiEcommerceAgent",
                    "capabilities": ["ecommerce_support", "conversation_memory"]
                }
                await websocket.send(json.dumps(greeting))

                # Listen for messages from target
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        print(f"🎯 Target message: {data}")

                        # If it's a test message, respond
                        if data.get('type') == 'test_query':
                            test_response = await self.generate_response(data.get('message', ''))
                            response = {
                                "type": "test_response",
                                "response": test_response,
                                "agent": "GeminiEcommerceAgent"
                            }
                            await websocket.send(json.dumps(response))

                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON from target: {message}")
                    except Exception as e:
                        print(f"❌ Error handling target message: {e}")

        except Exception as e:
            print(f"❌ Failed to connect to target WebSocket: {e}")
            print("The agent will continue running its own WebSocket server.")

    async def start(self):
        """
        Start the Gemini e-commerce agent with both server and optional target connection.
        """
        print("🚀 Starting Gemini E-Commerce Agent...")

        # Start WebSocket server
        server = await websockets.serve(
            self.handle_websocket_connection,
            "localhost",
            self.port,
            ping_interval=30,
            ping_timeout=10
        )

        print(f"✅ WebSocket server started on ws://localhost:{self.port}")

        # Create tasks for both server and optional target connection
        tasks = [
            server.wait_closed(),  # Keep server running
        ]

        # Only connect to target if it's a different URL than our own server
        our_url = f"ws://localhost:{self.port}"
        if self.websocket_url != our_url and self.websocket_url != f"ws://localhost:{self.port}/ws":
            try:
                target_task = asyncio.create_task(self.connect_to_target_websocket())
                tasks.append(target_task)
            except Exception as e:
                print(f"⚠️  Target WebSocket connection failed: {e}")
        else:
            print("ℹ️  Skipping target connection (same as server URL)")

        # Run all tasks
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down agent...")
        finally:
            server.close()
            await server.wait_closed()
            print("👋 Agent shutdown complete")


async def main():
    """Main entry point for the Azure OpenAI e-commerce agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Azure OpenAI E-Commerce Assistant Agent")
    parser.add_argument("--port", type=int, default=8001, help="Port for WebSocket server (default: 8001)")
    parser.add_argument("--target", type=str, default="ws://localhost:8000/ws",
                       help="Target WebSocket URL to connect to (default: ws://localhost:8000/ws)")

    args = parser.parse_args()

    # Create and start agent
    agent = AzureEcommerceAgent(
        websocket_url=args.target,
        port=args.port
    )

    await agent.start()


if __name__ == "__main__":
    # Run the agent
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)