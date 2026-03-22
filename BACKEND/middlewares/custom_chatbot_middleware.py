import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import websockets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ─── Selectors for Target Chatbot (app.jsx) ──────────────────────────────────
# Target Chatbot Backend is now on 8005, and UI usually maps to its own dev port (e.g. 3000)
# But if the middleware connects to the UI, we keep the TARGET_URL.
# If the logic needs the browser to point to a specific port:
TARGET_URL       = "http://localhost:3000" 
# ────────────────────────────────────────────────────────────────────────────
INPUT_SELECTOR   = "textarea#chat-textarea"
SEND_BTN_SELECTOR = "button#send-button"
ATTACH_BTN_ID    = "attach-button"
IMAGE_INPUT_ID   = "image-input"
# Message container and specific message tracking
MESSAGES_CONTAINER_SELECTOR = "#chat-messages-container"
# We'll use a dynamic selector to find the latest assistant bubble
BOT_BUBBLE_PREFIX = "bot-bubble-"
TYPING_INDICATOR_ID     = "bot-typing-indicator"
IMAGE_INPUT_ID          = "image-input"
# ────────────────────────────────────────────────────────────────────────────

class TargetChatbotAutomation:
    """
    Selenium driver to automate the Target Chatbot React UI.
    """
    def __init__(self, headless: bool = False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def start(self):
        logger.info(f"Opening {TARGET_URL}...")
        self.driver.get(TARGET_URL)
        # Wait for React to mount and input to be present
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, INPUT_SELECTOR)))
        logger.info("✅ Target Chatbot UI loaded and ready.")

    def send_message(self, text: str, image_path: str = None):
        """
        Sends a message, optionally attaching an image first.
        """
        logger.info(f"Sending message: {text} (Image: {image_path})")
        try:
            # 1. Handle image attachment if provided
            if image_path:
                logger.info(f"Attaching image without media picker UI: {image_path}")
                
                # Directly send the path to the file input (standard automation bypass for speed/stability)
                file_input = self.driver.find_element(By.ID, IMAGE_INPUT_ID)
                
                # Temporarily unhide the input purely for Selenium's internal validation, 
                # but we DO NOT click the clip button anymore.
                self.driver.execute_script(
                    "arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", 
                    file_input
                )
                
                # Upload the file directly
                file_input.send_keys(image_path)
                
                # Wait for the image preview to appear (confirming React state update)
                logger.info("Waiting for image preview (preview-thumb) to appear...")
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "preview-thumb")))
                
                # Reset styles immediately
                self.driver.execute_script("arguments[0].style.display = 'none';", file_input)
                
                # Focus text area
                try:
                    input_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, INPUT_SELECTOR)))
                    input_field.click()
                except:
                    pass

                time.sleep(1.0)
                logger.info("✅ Image attached silently via background input.")

            # 2. Wait for field to be ready
            input_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, INPUT_SELECTOR)))
            input_field.clear()
            input_field.send_keys(text)
            
            # 3. Click send button
            send_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEND_BTN_SELECTOR)))
            send_btn.click()
        except Exception as e:
            logger.error(f"Failed to send message via Selenium: {e}")
            raise

    def get_latest_response(self, timeout=30):
        logger.info("Waiting for bot response...")
        
        # 1. First, wait for the typing indicator to APPEAR
        # This confirms the bot received the message and is processing
        start_time = time.time()
        typing_detected = False
        while time.time() - start_time < 5: # Short timeout for typing to start
            try:
                typing = self.driver.find_elements(By.ID, TYPING_INDICATOR_ID)
                if typing and typing[0].is_displayed():
                    logger.info("📡 Bot typing indicator detected...")
                    typing_detected = True
                    break
            except:
                pass
            time.sleep(0.2)

        # 2. Extract a snapshot of current assistant bubbles to ensure we pick the NEWEST one
        all_bubbles = self.driver.find_elements(By.XPATH, "//*[starts-with(@id, 'bot-bubble-')]")
        initial_count = len(all_bubbles)
        logger.info(f"Currently have {initial_count} bubbles. Waiting for next message...")

        # 3. Now wait for the indicator to DISAPPEAR and the text to be ready
        while time.time() - start_time < timeout:
            try:
                # Refresh bubbles list
                current_bubbles = self.driver.find_elements(By.XPATH, "//*[starts-with(@id, 'bot-bubble-')]")
                
                # Check typing status
                is_typing = False
                try:
                    typing = self.driver.find_elements(By.ID, TYPING_INDICATOR_ID)
                    if typing and typing[0].is_displayed():
                        is_typing = True
                except:
                    pass

                # If we have a new bubble and typing stopped (or if we are on the first message)
                if len(current_bubbles) > initial_count or (initial_count == 0 and len(current_bubbles) > 0):
                    latest_bubble = current_bubbles[-1]
                    text = latest_bubble.text.strip()
                    
                    if text and text != "..." and not text.startswith("Connecting") and not is_typing:
                        logger.info(f"✅ Extracted response: {text[:60]}...")
                        return text
            except Exception as e:
                pass
            
            time.sleep(0.5)
        
        # Fallback: Just return the last bubble if we timed out but something is visible
        try:
            final_check = self.driver.find_elements(By.XPATH, "//*[starts-with(@id, 'bot-bubble-')]")
            if final_check:
                return final_check[-1].text.strip()
        except:
            pass

        raise TimeoutError("Timed out waiting for bot to finish response")

    def stop(self):
        self.driver.quit()

async def middleware_server(host="localhost", port=8005):
    """
    Middleware server that listens for WebSocket commands and executes them via Selenium.
    """
    automation = TargetChatbotAutomation(headless=False)
    automation.start()

    async def handle_client(websocket, path=None):
        remote_addr = websocket.remote_address
        logger.info(f"Client connected: {remote_addr}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    prompt = data.get("prompt", data.get("message", ""))
                    image_path = data.get("image_path") # Optional path to image file
                    
                    if not prompt and not image_path:
                        await websocket.send(json.dumps({"error": "No prompt or image path provided"}))
                        continue
                    
                    # Execute automation
                    try:
                        automation.send_message(prompt, image_path)
                        response_text = automation.get_latest_response()
                        
                        # Log and return response
                        print(f"\n[MIDDLEWARE LOG] Response from Chatbot: {response_text}\n")
                        
                        await websocket.send(json.dumps({
                            "status": "success",
                            "response": response_text,
                            "timestamp": datetime.now().isoformat()
                        }))
                    except Exception as auto_err:
                        logger.error(f"Automation error: {auto_err}")
                        await websocket.send(json.dumps({"error": f"Automation failed: {str(auto_err)}"}))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    # Try to send error to client before websocket closes
                    try:
                        await websocket.send(json.dumps({"error": str(e)}))
                    except:
                        pass
                    
        except Exception as e:
            logger.info(f"Client connection handling stopped: {remote_addr} ({e})")
        finally:
            pass

    logger.info(f"🚀 Middleware listening on ws://{host}:{port}")
    # Middleware now listens on 8001 to act as the primary target for Red Teaming
    async with websockets.serve(handle_client, host, 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(middleware_server())
    except KeyboardInterrupt:
        logger.info("Shutting down middleware...")
