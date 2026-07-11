"""
WebSocket Middleware Server for Target Chatbot UI Integration.

This middleware exposes a WebSocket /chat endpoint for api_server.py and
forwards messages to the Target Chatbot frontend UI through Selenium.

Element IDs used from Target Chatbot frontend:
- Input field  : id="chat-textarea"
- Send button  : id="send-button"
- Bot bubbles  : id="bot-bubble-<index>"
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

import websockets
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Add BACKEND root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            str(_LOG_DIR / f"target_ui_middleware_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)


TARGET_UI_URL = os.getenv("TARGET_CHATBOT_UI_URL", "http://localhost:3000")
INPUT_FIELD_ID = "chat-textarea"
SEND_BUTTON_ID = "send-button"
BOT_BUBBLE_PREFIX = "bot-bubble-"


def _get_float_env(name: str, default: float, minimum: float = 0.0) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return max(minimum, float(raw))
    except ValueError:
        logger.warning("[TargetUI] Invalid %s=%s. Using default %s", name, raw, default)
        return default


PAGE_STABILIZATION_SECONDS = _get_float_env("TARGET_UI_STABILIZATION_SECONDS", 2.0)
CONTROL_READY_TIMEOUT_SECONDS = _get_float_env("TARGET_UI_CONTROL_READY_TIMEOUT_SECONDS", 2.0, 1.0)
CONTROL_READY_POLL_SECONDS = _get_float_env("TARGET_UI_CONTROL_READY_POLL_SECONDS", 2.0, 0.2)
RESPONSE_RENDER_WAIT_SECONDS = _get_float_env("E_COMMERCE_RESPONSE_WAIT_SECONDS", 2.0)

DEAD_SESSION_MARKERS = (
    "invalid session id",
    "session deleted as the browser has closed the connection",
    "not connected to devtools",
    "disconnected",
    "chrome not reachable",
    "no such window",
    "target window already closed",
)


class TargetChatbotUIDriver:
    """Selenium automation for the Target Chatbot frontend."""

    def __init__(self, ui_url: str, headless: bool = False):
        self.ui_url = ui_url
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self._prev_bot_bubble_count = 0

    def _is_dead_session_error(self, exc: Exception) -> bool:
        if isinstance(exc, InvalidSessionIdException):
            return True
        if isinstance(exc, WebDriverException):
            message = str(exc).lower()
            return any(marker in message for marker in DEAD_SESSION_MARKERS)
        return False

    def _build_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1600,1000")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.page_load_strategy = "eager"

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(45)
        driver.implicitly_wait(2)
        return driver

    def connect(self) -> bool:
        """Open UI and verify key elements are present."""
        try:
            logger.info("[TargetUI] Launching browser")
            self.driver = self._build_driver()

            logger.info("[TargetUI] Navigating to %s", self.ui_url)
            self.driver.get(self.ui_url)

            if PAGE_STABILIZATION_SECONDS > 0:
                logger.info(
                    "[TargetUI] Waiting %.1fs for page stabilization...",
                    PAGE_STABILIZATION_SECONDS,
                )
                time.sleep(PAGE_STABILIZATION_SECONDS)

            textarea = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
            )
            send_button = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, SEND_BUTTON_ID))
            )

            logger.info(
                "[TargetUI] Waiting up to %.1fs for chat input to become enabled...",
                CONTROL_READY_TIMEOUT_SECONDS,
            )
            deadline = time.time() + CONTROL_READY_TIMEOUT_SECONDS
            while time.time() < deadline:
                textarea = self.driver.find_element(By.ID, INPUT_FIELD_ID)
                send_button = self.driver.find_element(By.ID, SEND_BUTTON_ID)

                # In this UI, send button stays disabled until text is entered.
                # Readiness should require only input to be interactive.
                if textarea.is_enabled():
                    logger.info(
                        "[TargetUI] Chat input is enabled (send button currently enabled=%s)",
                        send_button.is_enabled(),
                    )
                    break

                logger.info(
                    "[TargetUI] Chat input still disabled; waiting %.1fs...",
                    CONTROL_READY_POLL_SECONDS,
                )
                time.sleep(CONTROL_READY_POLL_SECONDS)
            else:
                logger.error(
                    "[TargetUI] UI loaded but chat input stayed disabled after %.1fs. "
                    "Target Chatbot frontend is likely not connected to its backend (expected ws://localhost:8005/ws).",
                    CONTROL_READY_TIMEOUT_SECONDS,
                )
                return False

            self._prev_bot_bubble_count = self._bot_bubble_count()
            logger.info(
                "[TargetUI] Connected. Baseline assistant bubbles=%d",
                self._prev_bot_bubble_count,
            )
            return True
        except Exception as exc:
            logger.error("[TargetUI] connect failed: %s (%s)", exc, type(exc).__name__)
            self.disconnect()
            return False

    def reconnect(self) -> bool:
        """Rebuild browser session after detected driver death."""
        logger.warning("[TargetUI] Attempting browser session recovery")
        self.disconnect()
        return self.connect()

    def disconnect(self):
        """Close browser session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def _bot_bubble_count(self) -> int:
        if not self.driver:
            return 0
        elements = self.driver.find_elements(By.CSS_SELECTOR, f"[id^='{BOT_BUBBLE_PREFIX}']")
        return len(elements)

    def send_message(self, message: str) -> str:
        """Send message through the UI and return latest assistant response."""
        if not self.driver:
            return "[Error: Browser not initialized]"

        try:
            return self._send_message_once(message)
        except Exception as exc:
            if self._is_dead_session_error(exc):
                logger.warning("[TargetUI] Detected dead Selenium session: %s", exc)
                recovered = self.reconnect()
                if recovered:
                    try:
                        logger.info("[TargetUI] Recovery succeeded. Retrying current message once")
                        return self._send_message_once(message)
                    except Exception as retry_exc:
                        logger.error("[TargetUI] Retry after recovery failed: %s", retry_exc)
                        return f"[Error: {retry_exc}]"
                return "[Error: Browser session was lost and automatic recovery failed]"

            logger.error("[TargetUI] send_message error: %s", exc)
            return f"[Error: {exc}]"

    def _send_message_once(self, message: str) -> str:
        """Single send attempt; caller is responsible for recovery policy."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        textarea = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
        )
        send_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, SEND_BUTTON_ID))
        )

        prev_count = self._bot_bubble_count()

        textarea.click()
        time.sleep(0.15)
        textarea.send_keys(Keys.CONTROL, "a")
        textarea.send_keys(Keys.DELETE)
        textarea.send_keys(message)

        # Prefer clicking send when enabled; fallback to Enter key if button remains disabled.
        if send_button.is_enabled():
            send_button.click()
        else:
            textarea.send_keys(Keys.ENTER)
        logger.info("[TargetUI] Sent message: %s", message[:120])

        def bot_response_arrived(driver):
            return len(driver.find_elements(By.CSS_SELECTOR, f"[id^='{BOT_BUBBLE_PREFIX}']")) > prev_count

        WebDriverWait(self.driver, 60).until(bot_response_arrived)
        if RESPONSE_RENDER_WAIT_SECONDS > 0:
            logger.info(
                "[TargetUI] Waiting %.1fs for response text rendering...",
                RESPONSE_RENDER_WAIT_SECONDS,
            )
            time.sleep(RESPONSE_RENDER_WAIT_SECONDS)

        bubbles = self.driver.find_elements(By.CSS_SELECTOR, f"[id^='{BOT_BUBBLE_PREFIX}']")
        if not bubbles:
            return "[Error: No assistant response found]"

        last_response = bubbles[-1].text.strip()
        self._prev_bot_bubble_count = len(bubbles)
        logger.info("[TargetUI] Received response: %s", last_response[:120])
        return last_response or "[Error: Assistant response is empty]"

    def reset_conversation(self):
        """Reload the page to reset conversation state."""
        if not self.driver:
            return
        try:
            self.driver.get(self.ui_url)
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
            )
            self._prev_bot_bubble_count = self._bot_bubble_count()
            logger.info("[TargetUI] Conversation reset complete")
        except Exception as exc:
            if self._is_dead_session_error(exc):
                logger.warning("[TargetUI] Session lost during reset. Attempting recovery")
                if self.reconnect():
                    logger.info("[TargetUI] Recovery after reset failure succeeded")
                    return
            logger.error("[TargetUI] reset failed: %s", exc)


class TargetChatbotUIMiddleware:
    """WebSocket server exposing Target Chatbot UI as a chat endpoint."""

    def __init__(self, ui_url: str, headless: bool = False):
        self.ui_url = ui_url
        self.headless = headless
        self.driver: Optional[TargetChatbotUIDriver] = None
        self.connected = False
        self.active_connections: Set = set()
        self._ui_lock = asyncio.Lock()

        self.total_messages = 0
        self.successful_messages = 0
        self.failed_messages = 0

    async def initialise(self) -> bool:
        logger.info("=" * 80)
        logger.info("INITIALIZING TARGET CHATBOT UI MIDDLEWARE")
        logger.info("=" * 80)
        logger.info("UI URL  : %s", self.ui_url)
        logger.info("Headless: %s", self.headless)

        self.driver = TargetChatbotUIDriver(ui_url=self.ui_url, headless=self.headless)
        success = await asyncio.to_thread(self.driver.connect)

        if success:
            self.connected = True
            logger.info("[Middleware] Target Chatbot UI connected and ready")
            return True

        logger.error("[Middleware] Failed to initialize Target Chatbot UI")
        return False

    async def cleanup(self):
        logger.info("[Middleware] Cleaning up")

        for ws in list(self.active_connections):
            try:
                await ws.close()
            except Exception:
                pass

        if self.driver:
            await asyncio.to_thread(self.driver.disconnect)

        logger.info("[Middleware] Cleanup complete")

    async def handle_client(self, websocket):
        self.active_connections.add(websocket)
        client = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info("[Middleware] Client connected: %s", client)

        try:
            await websocket.send(json.dumps({
                "type": "connection",
                "message": "Connected to Target Chatbot UI Middleware",
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
            }))

            async for raw in websocket:
                await self._process_message(websocket, raw)

        except websockets.exceptions.ConnectionClosedError as exc:
            logger.warning("[Middleware] Connection closed by %s: %s", client, exc)
        except Exception as exc:
            logger.error("[Middleware] Error with %s: %s", client, exc)
        finally:
            self.active_connections.discard(websocket)
            logger.info("[Middleware] Client disconnected: %s", client)

    async def _process_message(self, websocket, raw: str):
        self.total_messages += 1

        try:
            data = json.loads(raw)
            msg_type = data.get("type", "unknown")
            user_msg = data.get("message", "")
            thread_id = data.get("thread_id", "unknown")

            if msg_type == "query" and user_msg:
                if not self.connected or not self.driver:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Target Chatbot UI is not connected",
                        "timestamp": datetime.now().isoformat(),
                    }))
                    self.failed_messages += 1
                    return

                try:
                    async with self._ui_lock:
                        response_text = await asyncio.wait_for(
                            asyncio.to_thread(self.driver.send_message, user_msg),
                            timeout=90.0,
                        )
                except asyncio.TimeoutError:
                    response_text = "[Error: Timeout waiting for Target Chatbot UI response (90s)]"
                    self.failed_messages += 1

                await websocket.send(json.dumps({
                    "type": "response",
                    "message": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "thread_id": thread_id,
                }))
                self.successful_messages += 1
                return

            if msg_type == "reset":
                if self.driver:
                    async with self._ui_lock:
                        await asyncio.to_thread(self.driver.reset_conversation)
                await websocket.send(json.dumps({
                    "type": "response",
                    "message": "Conversation reset",
                    "timestamp": datetime.now().isoformat(),
                }))
                return

            if msg_type == "ping":
                await websocket.send(json.dumps({
                    "type": "pong",
                    "message": "Target UI middleware is alive",
                    "timestamp": datetime.now().isoformat(),
                }))
                return

            self.failed_messages += 1
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {msg_type}",
                "timestamp": datetime.now().isoformat(),
            }))

        except json.JSONDecodeError as exc:
            self.failed_messages += 1
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Invalid JSON: {exc}",
                "timestamp": datetime.now().isoformat(),
            }))
        except Exception as exc:
            self.failed_messages += 1
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Processing error: {exc}",
                "timestamp": datetime.now().isoformat(),
            }))

    def print_stats(self):
        logger.info("=" * 80)
        logger.info("TARGET CHATBOT UI MIDDLEWARE STATS")
        logger.info("Total messages: %d", self.total_messages)
        logger.info("Successful    : %d", self.successful_messages)
        logger.info("Failed        : %d", self.failed_messages)
        logger.info("Active conns  : %d", len(self.active_connections))
        if self.total_messages:
            success_rate = (self.successful_messages / self.total_messages) * 100
            logger.info("Success rate  : %.1f%%", success_rate)
        logger.info("=" * 80)


async def start_target_ui_middleware(
    ui_url: str,
    host: str = "localhost",
    port: int = 8002,
    headless: bool = False,
):
    """Start the Target Chatbot UI middleware WebSocket server."""
    middleware = TargetChatbotUIMiddleware(ui_url=ui_url, headless=headless)

    if not await middleware.initialise():
        logger.error("Could not initialize middleware")
        return

    logger.info("=" * 80)
    logger.info("TARGET CHATBOT UI MIDDLEWARE STARTED")
    logger.info("WebSocket: ws://%s:%d/chat", host, port)
    logger.info("UI URL   : %s", ui_url)
    logger.info("=" * 80)

    try:
        async with websockets.serve(middleware.handle_client, host, port):
            await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        middleware.print_stats()
        await middleware.cleanup()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Target Chatbot UI WebSocket Middleware"
    )
    parser.add_argument(
        "--url",
        default=TARGET_UI_URL,
        help="Target Chatbot frontend URL (default from TARGET_CHATBOT_UI_URL or http://localhost:3000)",
    )
    parser.add_argument("--host", default="localhost", help="Middleware host")
    parser.add_argument("--port", type=int, default=8002, help="Middleware port")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless")
    args = parser.parse_args()

    asyncio.run(
        start_target_ui_middleware(
            ui_url=args.url,
            host=args.host,
            port=args.port,
            headless=args.headless,
        )
    )
