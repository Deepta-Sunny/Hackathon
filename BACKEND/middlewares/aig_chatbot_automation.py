"""
WebSocket Middleware Server for Air India Ai.g Chatbot Integration

This middleware bridges the gap between api_server.py (which expects WebSocket chatbots)
and the Ai.g web chatbot on Air India's website.

Architecture:
- api_server.py connects to this middleware WebSocket server
- Middleware keeps the Ai.g chatbot open using Selenium automation
- Receives attack prompts via WebSocket protocol
- Pastes prompts into the Ai.g chat input field
- Extracts responses from the webpage
- Returns responses via WebSocket protocol

Key selectors (hardcoded from DOM inspection):
- Cookie popup button : id="onetrust-accept-btn-handler"
- Chatbot icon        : id="ask-aig"  (img in main document, JS click needed)
- Chat input field    : id="inputChat" (textarea in main document, no iframe)
- Bot response        : .bot-chat-content p.child
"""

import asyncio
import json
import time
import sys
import logging
import websockets
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Add BACKEND root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure logs directory exists
_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

# Configure UTF-8 encoding for console output on Windows to support emoji characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            str(_LOG_DIR / f"aig_middleware_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            encoding='utf-8'
        ),
    ],
)
logger = logging.getLogger(__name__)

# ─── Hardcoded selectors ────────────────────────────────────────────────────
AIRINDIA_URL      = "https://www.airindia.com/"
COOKIE_BTN_ID     = "onetrust-accept-btn-handler"
CHATBOT_ICON_ID   = "ask-aig"
INPUT_FIELD_ID    = "inputChat"
BOT_MSG_SELECTOR  = ".bot-chat-content p.child"
# ────────────────────────────────────────────────────────────────────────────


class AigChatbotDriver:
    """
    Selenium driver that connects to and interacts with the Air India Ai.g chatbot.
    Encapsulates all browser automation so the middleware stays clean.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self._prev_bot_msg_count: int = 0
        self._screenshot_dir = Path(__file__).parent.parent / "logs" / "screenshots"
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

    # ── browser lifecycle ──────────────────────────────────────────────────

    def _save_debug_screenshot(self, name: str = "debug"):
        """Save a screenshot for debugging purposes."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self._screenshot_dir / f"{name}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"[Ai.g Driver] 📸 Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.warning(f"[Ai.g Driver] Failed to save screenshot: {e}")
            return None

    def _save_page_source(self, name: str = "debug"):
        """Save page HTML source for debugging."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source_path = self._screenshot_dir / f"{name}_{timestamp}.html"
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"[Ai.g Driver] 📄 Page source saved: {source_path}")
            return str(source_path)
        except Exception as e:
            logger.warning(f"[Ai.g Driver] Failed to save page source: {e}")
            return None

    def _build_driver(self) -> webdriver.Chrome:
        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.page_load_strategy = "eager"
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)

    def connect(self) -> bool:
        """Open browser, navigate to Air India and activate the Ai.g chat window."""
        try:
            logger.info("[Ai.g Driver] Initialising Chrome...")
            self.driver = self._build_driver()
            self.driver.set_page_load_timeout(30)

            logger.info(f"[Ai.g Driver] Navigating to {AIRINDIA_URL} ...")
            try:
                self.driver.get(AIRINDIA_URL)
            except Exception as e:
                logger.warning(f"[Ai.g Driver] Page load timeout (continuing): {str(e)[:80]}")

            # Wait for page to settle
            logger.info("[Ai.g Driver] Waiting for page stabilisation (15s)...")
            time.sleep(15)

            # ── Dismiss cookie popup if present ──────────────────────────
            logger.info("[Ai.g Driver] Checking for cookie consent popup...")
            try:
                cookie_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, COOKIE_BTN_ID))
                )
                cookie_btn.click()
                logger.info("[Ai.g Driver] ✅ Cookie consent dismissed.")
                time.sleep(1)
            except Exception:
                logger.info("[Ai.g Driver] No cookie popup found, continuing.")

            # ── Click chatbot icon via JS (img element, normal click intercepted) ──
            logger.info(f"[Ai.g Driver] Searching for chatbot icon (id='{CHATBOT_ICON_ID}')...")
            icon_clicked = False
            
            # Try Method 1: Find by ID
            try:
                logger.info("[Ai.g Driver] Method 1: Looking for element by ID...")
                icon = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, CHATBOT_ICON_ID))
                )
                logger.info(f"[Ai.g Driver] Icon found! Tag: {icon.tag_name}, Displayed: {icon.is_displayed()}")
                
                # Try scrolling to element first
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", icon)
                time.sleep(1)
                
                # Try multiple click methods
                for method_name, click_func in [
                    ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", icon)),
                    ("JavaScript with event", lambda: self.driver.execute_script(
                        "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", icon
                    )),
                    ("Regular click", lambda: icon.click()),
                ]:
                    try:
                        click_func()
                        logger.info(f"[Ai.g Driver] ✅ {method_name} executed")
                        icon_clicked = True
                        break
                    except Exception as e:
                        logger.warning(f"[Ai.g Driver] {method_name} failed: {str(e)[:100]}")
                
            except Exception as e:
                logger.warning(f"[Ai.g Driver] Method 1 failed: {str(e)[:100]}")
            
            # Try Method 2: Search by img alt text or other attributes
            if not icon_clicked:
                try:
                    logger.info("[Ai.g Driver] Method 2: Searching by img tags with 'aig' in src/alt...")
                    imgs = self.driver.find_elements(By.TAG_NAME, "img")
                    for img in imgs:
                        src = (img.get_attribute('src') or '').lower()
                        alt = (img.get_attribute('alt') or '').lower()
                        img_id = (img.get_attribute('id') or '').lower()
                        if 'aig' in src or 'aig' in alt or 'aig' in img_id or 'chat' in alt:
                            logger.info(f"[Ai.g Driver] Found potential chatbot: src={src[:50]}, alt={alt}, id={img_id}")
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
                            time.sleep(0.5)
                            try:
                                self.driver.execute_script("arguments[0].click();", img)
                                logger.info("[Ai.g Driver] ✅ Clicked potential chatbot icon")
                                icon_clicked = True
                                break
                            except:
                                pass
                except Exception as e:
                    logger.warning(f"[Ai.g Driver] Method 2 failed: {e}")
            
            # Try Method 3: Look for clickable elements with chat-related classes
            if not icon_clicked:
                try:
                    logger.info("[Ai.g Driver] Method 3: Searching for chat-related clickable elements...")
                    chat_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "[class*='chat'], [class*='bot'], [id*='chat'], [id*='bot']")
                    for elem in chat_elements[:10]:
                        try:
                            if elem.is_displayed():
                                elem_id = elem.get_attribute('id') or 'no-id'
                                elem_class = elem.get_attribute('class') or 'no-class'
                                logger.info(f"[Ai.g Driver] Trying: {elem.tag_name}, id={elem_id}, class={elem_class[:50]}")
                                self.driver.execute_script("arguments[0].click();", elem)
                                icon_clicked = True
                                logger.info("[Ai.g Driver] ✅ Clicked chat element")
                                break
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"[Ai.g Driver] Method 3 failed: {e}")
            
            if not icon_clicked:
                logger.error("[Ai.g Driver] ❌ All methods to click chatbot icon failed!")
                self._save_debug_screenshot("chatbot_icon_all_methods_failed")
                self._save_page_source("chatbot_icon_all_methods_failed")
            else:
                logger.info("[Ai.g Driver] Waiting for chat window to appear (10s)...")
                time.sleep(10)

            # ── Verify input field is visible ────────────────────────────
            logger.info(f"[Ai.g Driver] Waiting for input field (id='{INPUT_FIELD_ID}')...")
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
                )
                logger.info("[Ai.g Driver] ✅ Chat input field is visible — ready!")
            except Exception as e:
                logger.error(f"[Ai.g Driver] ❌ Chat input field not found: {e}")
                self._save_debug_screenshot("input_field_not_found")
                self._save_page_source("input_field_not_found")
                
                # Debug: Try to find similar input elements
                try:
                    logger.info("[Ai.g Driver] Searching for alternative input fields...")
                    all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea")
                    logger.info(f"[Ai.g Driver] Found {len(all_inputs)} input/textarea elements on page")
                    for inp in all_inputs[:10]:  # Show first 10
                        try:
                            inp_id = inp.get_attribute('id') or 'no-id'
                            inp_type = inp.get_attribute('type') or inp.tag_name
                            inp_placeholder = inp.get_attribute('placeholder') or ''
                            if inp.is_displayed():
                                logger.info(f"  - Visible: {inp_type}, ID: {inp_id}, Placeholder: {inp_placeholder[:50]}")
                        except:
                            pass
                except Exception as debug_err:
                    logger.warning(f"[Ai.g Driver] Debug search failed: {debug_err}")
                
                # Check for iframes
                try:
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                    logger.info(f"[Ai.g Driver] Found {len(iframes)} iframe(s) on page")
                    for idx, iframe in enumerate(iframes[:3]):
                        try:
                            iframe_src = iframe.get_attribute('src') or 'no-src'
                            iframe_id = iframe.get_attribute('id') or 'no-id'
                            logger.info(f"  - Iframe {idx}: ID={iframe_id}, Src={iframe_src[:100]}")
                        except:
                            pass
                except Exception as debug_err:
                    logger.warning(f"[Ai.g Driver] Iframe check failed: {debug_err}")
                
                return False

            # Snapshot current bot message count as baseline
            self._prev_bot_msg_count = len(
                self.driver.find_elements(By.CSS_SELECTOR, BOT_MSG_SELECTOR)
            )

            return True

        except Exception as e:
            logger.error(f"[Ai.g Driver] Connection failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def disconnect(self):
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    # ── messaging ──────────────────────────────────────────────────────────

    def send_message(self, message: str) -> str:
        """
        Type *message* into the Ai.g chat input, press Enter and wait for the
        bot reply.  Returns the bot's response text (or an error string).
        """
        if not self.driver:
            return "[Error: Browser not initialised]"

        try:
            # ── Find and fill the input field ────────────────────────────
            input_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
            )
            input_field.click()
            time.sleep(0.3)
            input_field.clear()
            input_field.send_keys(message)
            time.sleep(0.3)
            input_field.send_keys(Keys.RETURN)
            logger.info(f"[Ai.g Driver] ✅ Sent: {message[:80]}")

            # ── Wait for a new bot response ───────────────────────────────
            prev_count = self._prev_bot_msg_count

            def new_msg_appeared(driver):
                msgs = driver.find_elements(By.CSS_SELECTOR, BOT_MSG_SELECTOR)
                return len(msgs) > prev_count

            WebDriverWait(self.driver, 30).until(new_msg_appeared)

            all_msgs = self.driver.find_elements(By.CSS_SELECTOR, BOT_MSG_SELECTOR)
            response = all_msgs[-1].text.strip() if all_msgs else "[Error: No response found]"
            self._prev_bot_msg_count = len(all_msgs)

            logger.info(f"[Ai.g Driver] ✅ Response: {response[:100]}")
            return response

        except Exception as e:
            logger.error(f"[Ai.g Driver] send_message error: {e}")
            return f"[Error: {str(e)}]"

    def reset_conversation(self):
        """
        Reload the page and reopen the chatbot to start a fresh conversation.
        """
        logger.info("[Ai.g Driver] Resetting conversation (reloading page)...")
        try:
            self.driver.get(AIRINDIA_URL)
            time.sleep(15)

            # Dismiss cookie popup if it reappears
            try:
                cookie_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, COOKIE_BTN_ID))
                )
                cookie_btn.click()
                time.sleep(1)
            except Exception:
                pass

            # Reopen chat
            icon = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, CHATBOT_ICON_ID))
            )
            self.driver.execute_script("arguments[0].click();", icon)
            time.sleep(5)

            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, INPUT_FIELD_ID))
            )
            self._prev_bot_msg_count = len(
                self.driver.find_elements(By.CSS_SELECTOR, BOT_MSG_SELECTOR)
            )
            logger.info("[Ai.g Driver] ✅ Conversation reset complete.")
        except Exception as e:
            logger.error(f"[Ai.g Driver] Reset failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
#  Middleware WebSocket server
# ═══════════════════════════════════════════════════════════════════════════

class AigChatbotMiddleware:
    """WebSocket server that exposes the Ai.g chatbot to api_server.py."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.aig: Optional[AigChatbotDriver] = None
        self.active_connections: Set = set()
        self.connected = False

        # Stats
        self.total_messages = 0
        self.successful_messages = 0
        self.failed_messages = 0

    # ── lifecycle ──────────────────────────────────────────────────────────

    async def initialise(self) -> bool:
        """Start the browser and open the Ai.g chatbot."""
        logger.info("=" * 80)
        logger.info("🌐 INITIALISING AI.G CHATBOT CONNECTION")
        logger.info("=" * 80)
        logger.info(f"Target : {AIRINDIA_URL}")
        logger.info(f"Headless: {self.headless}")
        logger.info("=" * 80)

        self.aig = AigChatbotDriver(headless=self.headless)

        # Run Selenium in a thread so it doesn't block the event loop
        success = await asyncio.to_thread(self.aig.connect)

        if success:
            self.connected = True
            logger.info("✅ Ai.g chatbot connected and ready!")

            # Warm-up test
            logger.info("🧪 Testing chatbot with 'hi' message...")
            try:
                test_resp = await asyncio.to_thread(self.aig.send_message, "hi")
                logger.info(f"✅ Warm-up response: {test_resp[:120]}")
                logger.info("✅ Chatbot automation verified!")
            except Exception as e:
                logger.warning(f"⚠️ Warm-up message failed: {e}. Will continue anyway.")

            logger.info("[Middleware] Waiting for api_server.py connections...")
            return True
        else:
            logger.error("❌ Failed to connect to Ai.g chatbot.")
            return False

    async def cleanup(self):
        """Close all WebSocket connections and the browser."""
        logger.info("🧹 Cleaning up middleware...")

        for ws in list(self.active_connections):
            try:
                await ws.close()
            except Exception:
                pass

        if self.aig:
            await asyncio.to_thread(self.aig.disconnect)

        logger.info("✅ Cleanup complete.")

    # ── WebSocket handler ──────────────────────────────────────────────────

    async def handle_client(self, websocket):
        self.active_connections.add(websocket)
        client = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"✅ [Middleware] New connection from {client}  "
                    f"(total: {len(self.active_connections)})")

        try:
            await websocket.send(json.dumps({
                "type": "connection",
                "message": "Connected to Ai.g Chatbot Middleware",
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
            }))

            async for raw in websocket:
                await self._process(websocket, raw)

        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"⚠️ [Middleware] Connection closed by {client}: {e}")
        except Exception as e:
            logger.error(f"❌ [Middleware] Error with {client}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self.active_connections.discard(websocket)
            logger.info(f"❌ [Middleware] Disconnected: {client}  "
                        f"(remaining: {len(self.active_connections)})")

    # ── message processing ─────────────────────────────────────────────────

    async def _process(self, websocket, raw: str):
        self.total_messages += 1
        try:
            data = json.loads(raw)
            msg_type  = data.get("type", "unknown")
            user_msg  = data.get("message", "")
            thread_id = data.get("thread_id", "unknown")

            logger.info(f"📨 [{msg_type}] thread={thread_id[:8]}…  msg={user_msg[:80]}")

            # ── query ────────────────────────────────────────────────────
            if msg_type == "query" and user_msg:
                if not self.connected or not self.aig:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Ai.g chatbot not connected",
                        "timestamp": datetime.now().isoformat(),
                    }))
                    self.failed_messages += 1
                    return

                try:
                    response_text = await asyncio.wait_for(
                        asyncio.to_thread(self.aig.send_message, user_msg),
                        timeout=60.0,
                    )
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Timeout waiting for Ai.g response")
                    response_text = "[Error: Timeout waiting for Ai.g response (60s)]"
                    self.failed_messages += 1

                await websocket.send(json.dumps({
                    "type": "response",
                    "message": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "thread_id": thread_id,
                }))
                self.successful_messages += 1
                logger.info(f"✅ Response sent: {response_text[:100]}")

            # ── reset ─────────────────────────────────────────────────────
            elif msg_type == "reset":
                if self.aig:
                    await asyncio.to_thread(self.aig.reset_conversation)
                await websocket.send(json.dumps({
                    "type": "response",
                    "message": "Conversation reset",
                    "timestamp": datetime.now().isoformat(),
                }))

            # ── ping ──────────────────────────────────────────────────────
            elif msg_type == "ping":
                await websocket.send(json.dumps({
                    "type": "pong",
                    "message": "Ai.g Middleware is alive",
                    "timestamp": datetime.now().isoformat(),
                }))

            # ── unknown ───────────────────────────────────────────────────
            else:
                logger.warning(f"⚠️ Unknown message type: {msg_type}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                    "timestamp": datetime.now().isoformat(),
                }))
                self.failed_messages += 1

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Invalid JSON: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }))
            self.failed_messages += 1
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Processing error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }))
            self.failed_messages += 1

    # ── stats ──────────────────────────────────────────────────────────────

    def print_stats(self):
        logger.info("=" * 80)
        logger.info("📊 AI.G MIDDLEWARE STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Total Messages : {self.total_messages}")
        logger.info(f"Successful     : {self.successful_messages}")
        logger.info(f"Failed         : {self.failed_messages}")
        if self.total_messages > 0:
            rate = (self.successful_messages / self.total_messages) * 100
            logger.info(f"Success Rate   : {rate:.1f}%")
        logger.info(f"Active Conns   : {len(self.active_connections)}")
        logger.info("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════════════

async def start_aig_middleware(
    host: str = "localhost",
    port: int = 8002,
    headless: bool = False,
):
    """Start the Ai.g WebSocket middleware server."""
    middleware = AigChatbotMiddleware(headless=headless)

    if not await middleware.initialise():
        logger.error("❌ Failed to initialise Ai.g chatbot. Exiting.")
        return

    logger.info("=" * 80)
    logger.info("🚀 AI.G MIDDLEWARE SERVER STARTED")
    logger.info("=" * 80)
    logger.info(f"WebSocket URL : ws://{host}:{port}/chat")
    logger.info(f"Target        : {AIRINDIA_URL}")
    logger.info("Point api_server.py to the WebSocket URL above.")
    logger.info("Press Ctrl+C to stop.")
    logger.info("=" * 80)

    try:
        async with websockets.serve(middleware.handle_client, host, port):
            logger.info(f"✅ Server running on ws://{host}:{port}")
            await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        logger.info("⚠️ Shutdown signal received.")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        middleware.print_stats()
        await middleware.cleanup()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Air India Ai.g Chatbot WebSocket Middleware"
    )
    parser.add_argument(
        "--host", default="localhost", help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8002, help="Server port (default: 8002)"
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode"
    )

    args = parser.parse_args()

    asyncio.run(start_aig_middleware(
        host=args.host,
        port=args.port,
        headless=args.headless,
    ))