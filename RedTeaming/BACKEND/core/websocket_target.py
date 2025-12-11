"""
WebSocket target for communicating with the chatbot.
Handles connection management, retries, and message formatting.
"""

import json
import asyncio
import websockets
from uuid import uuid4
from typing import Dict, Optional

from config import WEBSOCKET_URL, WEBSOCKET_TIMEOUT, WEBSOCKET_MAX_RETRIES


class ChatbotWebSocketTarget:
    """
    WebSocket client for chatbot communication with robust error handling.
    
    Features:
    - Automatic reconnection with exponential backoff
    - Configurable timeouts and retries
    - Thread-based conversation management
    - Comprehensive statistics tracking
    """
    
    def __init__(
        self,
        url: str = WEBSOCKET_URL,
        timeout: float = WEBSOCKET_TIMEOUT,
        max_retries: int = WEBSOCKET_MAX_RETRIES
    ):
        self.url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.thread_id = str(uuid4())
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Statistics
        self.timeout_count = 0
        self.error_count = 0
        self.success_count = 0
        self.forbidden = False
    
    async def connect(self) -> bool:
        """
        Establish WebSocket connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.url),
                timeout=5.0
            )
            return True
        except websockets.exceptions.InvalidStatusCode as e:
            if e.status_code == 403:
                self.forbidden = True
                print(f"⚠️ Connection failed: server rejected WebSocket connection: HTTP {e.status_code}")
                return False
            else:
                print(f"⚠️ Connection failed: Invalid status code {e.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Connection failed: {e}")
            return False
    
    async def send_message(self, message: str) -> str:
        """
        Send message and receive response with retry logic.
        
        Args:
            message: The message to send to the chatbot
            
        Returns:
            str: The chatbot's response or error message
        """
        if self.forbidden:
            return "[Connection Error: server rejected WebSocket connection: HTTP 403]"
        
        for attempt in range(self.max_retries + 1):
            try:
                # Ensure connection is established
                if not self.websocket:
                    if not await self.connect():
                        if attempt < self.max_retries:
                            await asyncio.sleep(0.5 * (attempt + 1))
                            continue
                        self.error_count += 1
                        return "[Connection Error: Unable to establish WebSocket connection]"
                
                # Prepare payload matching the chatbot's expected format
                payload = json.dumps({
                    "type": "query",
                    "message": message,
                    "thread_id": self.thread_id
                })
                
                # Send message
                await self.websocket.send(payload)
                
                # Receive response with timeout
                try:
                    response = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.timeout
                    )
                except asyncio.CancelledError:
                    raise asyncio.TimeoutError("Operation cancelled")
                
                # Parse response
                result = self._parse_response(response)
                self.success_count += 1
                return result
                
            except asyncio.TimeoutError:
                self.websocket = None
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    self.timeout_count += 1
                    return f"[Timeout: No response after {self.max_retries + 1} attempts]"
            
            except asyncio.CancelledError:
                self.websocket = None
                self.error_count += 1
                return "[Error: Operation cancelled]"
            
            except websockets.exceptions.ConnectionClosed:
                self.websocket = None
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    self.error_count += 1
                    return "[Error: Connection closed by server]"
            
            except Exception as e:
                self.websocket = None
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    self.error_count += 1
                    return f"[Error: {str(e)[:100]}]"
        
        self.error_count += 1
        return "[Error: Max retries exceeded]"
    
    def _parse_response(self, response: str) -> str:
        """
        Parse WebSocket response based on message type.
        
        Args:
            response: Raw response string from WebSocket
            
        Returns:
            str: Parsed response message
        """
        try:
            data = json.loads(response)
            
            if data.get("type") == "response":
                return data.get("message", "")
            elif data.get("type") == "interrupt":
                return f"[INTERRUPT] {data.get('message', '')}"
            elif data.get("type") == "error":
                return f"[ERROR] {data.get('message', '')}"
            else:
                return data.get("message", data.get("content", str(data)))
                
        except json.JSONDecodeError:
            return response
    
    async def close(self):
        """Close WebSocket connection."""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            finally:
                self.websocket = None
    
    def reset_conversation(self):
        """Reset conversation with new thread ID for new attack run."""
        self.thread_id = str(uuid4())
    
    def get_stats(self) -> Dict:
        """
        Get connection statistics.
        
        Returns:
            Dict with success/timeout/error counts and success rate
        """
        total = self.success_count + self.timeout_count + self.error_count
        return {
            "total_attempts": total,
            "successful": self.success_count,
            "timeouts": self.timeout_count,
            "errors": self.error_count,
            "success_rate": f"{(self.success_count / total * 100):.1f}%" if total > 0 else "N/A"
        }
    
    def print_stats(self):
        """Print formatted connection statistics."""
        stats = self.get_stats()
        print(f"\n🔌 WebSocket Stats:")
        print(f"   • Total Attempts: {stats['total_attempts']}")
        print(f"   • Successful: {stats['successful']}")
        print(f"   • Timeouts: {stats['timeouts']}")
        print(f"   • Errors: {stats['errors']}")
        print(f"   • Success Rate: {stats['success_rate']}")
