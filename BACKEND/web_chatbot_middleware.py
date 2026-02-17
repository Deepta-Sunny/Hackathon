"""
WebSocket Middleware Server for Web-Based Chatbot Integration

This middleware bridges the gap between api_server.py (which expects WebSocket chatbots)
and web-based chatbots (like Tia on Air India Express).

Architecture:
- api_server.py connects to this middleware WebSocket server
- Middleware keeps the web chatbot open using Selenium automation
- Receives attack prompts via WebSocket protocol
- Pastes prompts into the web chatbot
- Extracts responses from the webpage
- Returns responses via WebSocket protocol
"""

import asyncio
import json
import websockets
import logging
from datetime import datetime
from typing import Optional, Dict, Set
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.web_screen_target import WebScreenTarget

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"middleware_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)


class WebChatbotMiddleware:
    """WebSocket server that provides WebSocket interface to web-based chatbots"""
    
    def __init__(self, target_url: str, headless: bool = False):
        """
        Initialize middleware
        
        Args:
            target_url: URL of the web chatbot (e.g., https://www.airindiaexpress.com/)
            headless: Whether to run browser in headless mode
        """
        self.target_url = target_url
        self.headless = headless
        self.web_target: Optional[WebScreenTarget] = None
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.connected = False
        
        # Statistics
        self.total_messages = 0
        self.successful_messages = 0
        self.failed_messages = 0
        
    async def initialize_web_target(self):
        """Initialize and connect to the web chatbot"""
        logger.info("="*80)
        logger.info("🌐 INITIALIZING WEB CHATBOT CONNECTION")
        logger.info("="*80)
        logger.info(f"Target URL: {self.target_url}")
        logger.info(f"Headless: {self.headless}")
        logger.info("="*80)
        
        self.web_target = WebScreenTarget(
            url=self.target_url,
            headless=self.headless
        )
        
        logger.info("🔗 Connecting to web chatbot...")
        success = await self.web_target.connect()
        
        if success:
            self.connected = True
            logger.info("✅ Web chatbot connected and ready!")
            
            # Send a test "hi" message to verify automation works
            logger.info("🧪 Testing chatbot with 'hi' message...")
            try:
                test_response = await self.web_target.send_message("hi")
                logger.info(f"✅ Test response received: {test_response[:100]}...")
                logger.info("✅ Chatbot automation verified!")
            except Exception as e:
                logger.warning(f"⚠️ Test message failed: {e}")
                logger.warning("Will continue anyway...")
            
            logger.info("[Middleware] Waiting for api_server.py connections...")
            return True
        else:
            logger.error("❌ Failed to connect to web chatbot")
            return False
    
    async def handle_client(self, websocket):
        """
        Handle incoming WebSocket connection from api_server.py
        
        Args:
            websocket: WebSocket connection
        """
        # Register connection
        self.active_connections.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        logger.info(f"✅ [Middleware] New connection from {client_info}")
        logger.info(f"   Active connections: {len(self.active_connections)}")
        
        try:
            # Send connection confirmation
            await websocket.send(json.dumps({
                "type": "connection",
                "message": "Connected to Web Chatbot Middleware",
                "status": "ready",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Handle messages
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"⚠️ [Middleware] Connection closed by {client_info}: {e}")
        except Exception as e:
            logger.error(f"❌ [Middleware] Error handling client {client_info}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # Unregister connection
            self.active_connections.discard(websocket)
            logger.info(f"❌ [Middleware] Client disconnected: {client_info}")
            logger.info(f"   Active connections: {len(self.active_connections)}")
    
    async def process_message(self, websocket, message: str):
        """
        Process incoming message from api_server.py
        
        Expected format from api_server.py:
        {
            "type": "query",
            "message": "attack prompt here",
            "thread_id": "uuid"
        }
        
        Args:
            websocket: WebSocket connection
            message: Incoming message string
        """
        self.total_messages += 1
        
        try:
            # Parse incoming message
            data = json.loads(message)
            msg_type = data.get("type", "unknown")
            user_message = data.get("message", "")
            thread_id = data.get("thread_id", "unknown")
            
            logger.info(f"📨 [Middleware] Received {msg_type} message (thread: {thread_id[:8]}...)")
            logger.info(f"   Message content: {user_message}") # Log full message
            
            if msg_type == "query" and user_message:
                # Forward message to web chatbot
                logger.info(f"   ⏳ Forwarding to web chatbot...")
                
                if not self.connected or not self.web_target:
                    error_response = {
                        "type": "error",
                        "message": "Web chatbot not connected",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(error_response))
                    self.failed_messages += 1
                    logger.error("   ❌ Web chatbot not connected")
                    return
                
                # Send to web chatbot with timeout (60 seconds)
                try:
                    response_text = await asyncio.wait_for(
                        self.web_target.send_message(user_message),
                        timeout=60.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"   ⚠️ Timeout waiting for web chatbot response")
                    response_text = "[Error: Timeout waiting for chatbot response after 60 seconds]"
                    self.failed_messages += 1
                
                logger.info(f"   ✅ Received response: {response_text}") # Log full response
                
                # Send response back to api_server.py
                response = {
                    "type": "response",
                    "message": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "thread_id": thread_id
                }
                
                await websocket.send(json.dumps(response))
                self.successful_messages += 1
                
                logger.info(f"   ✅ Response sent to api_server.py")
                
            elif msg_type == "reset":
                # Reset conversation
                logger.info(f"   🔄 Resetting conversation...")
                if self.web_target:
                    self.web_target.reset_conversation()
                
                response = {
                    "type": "response",
                    "message": "Conversation reset",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            elif msg_type == "ping":
                # Health check
                response = {
                    "type": "pong",
                    "message": "Middleware is alive",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            else:
                # Unknown message type
                logger.warning(f"   ⚠️ Unknown message type: {msg_type}")
                response = {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                self.failed_messages += 1
                
        except json.JSONDecodeError as e:
            logger.error(f"   ❌ JSON parse error: {e}")
            error_response = {
                "type": "error",
                "message": f"Invalid JSON: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_response))
            self.failed_messages += 1
            
        except Exception as e:
            logger.error(f"   ❌ Error processing message: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            error_response = {
                "type": "error",
                "message": f"Processing error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_response))
            self.failed_messages += 1
    
    def print_stats(self):
        """Print middleware statistics"""
        logger.info("="*80)
        logger.info("📊 MIDDLEWARE STATISTICS")
        logger.info("="*80)
        logger.info(f"Total Messages: {self.total_messages}")
        logger.info(f"Successful: {self.successful_messages}")
        logger.info(f"Failed: {self.failed_messages}")
        if self.total_messages > 0:
            success_rate = (self.successful_messages / self.total_messages) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Active Connections: {len(self.active_connections)}")
        logger.info("="*80)
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up middleware...")
        
        # Close all WebSocket connections
        if self.active_connections:
            logger.info(f"   Closing {len(self.active_connections)} active connections...")
            for ws in list(self.active_connections):
                try:
                    await ws.close()
                except:
                    pass
        
        # Close web target
        if self.web_target:
            logger.info("   Closing web browser...")
            await self.web_target.disconnect()
        
        logger.info("✅ Cleanup complete")


async def start_middleware_server(
    target_url: str,
    host: str = "localhost",
    port: int = 8001,
    headless: bool = False
):
    """
    Start the WebSocket middleware server
    
    Args:
        target_url: URL of the web chatbot
        host: Server host (default: localhost)
        port: Server port (default: 8001)
        headless: Run browser in headless mode
    """
    middleware = WebChatbotMiddleware(
        target_url=target_url,
        headless=headless
    )
    
    # Initialize web target first
    if not await middleware.initialize_web_target():
        logger.error("❌ Failed to initialize web chatbot. Exiting.")
        return
    
    logger.info("="*80)
    logger.info("🚀 STARTING WEBSOCKET MIDDLEWARE SERVER")
    logger.info("="*80)
    logger.info(f"WebSocket URL: ws://{host}:{port}/chat")
    logger.info(f"Target: {target_url}")
    logger.info(f"Ready to accept connections from api_server.py")
    logger.info("="*80)
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Start WebSocket server
        async with websockets.serve(middleware.handle_client, host, port):
            logger.info(f"✅ [Middleware] Server running on ws://{host}:{port}/chat")
            logger.info(f"[Middleware] Waiting for connections...")
            
            # Keep server running
            await asyncio.Future()  # Run forever
            
    except KeyboardInterrupt:
        logger.info("⚠️ Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        middleware.print_stats()
        await middleware.cleanup()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Chatbot WebSocket Middleware")
    parser.add_argument(
        "--url",
        default="https://www.airindiaexpress.com/",
        help="Target web chatbot URL (default: Air India Express)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Server port (default: 8001)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    args = parser.parse_args()
    
    # Run server
    asyncio.run(start_middleware_server(
        target_url=args.url,
        host=args.host,
        port=args.port,
        headless=args.headless
    ))
