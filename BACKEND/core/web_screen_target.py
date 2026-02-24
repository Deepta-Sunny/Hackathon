
import time
import json
import asyncio
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WebScreenTarget:
    """
    Selenium-based target for interacting with a chatbot on a website.
    """
    
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.headless = headless
        self.driver = None
        self.timeout = 60
        self.cached_iframe_index = None
        
        # Statistics
        self.success_count = 0
        self.error_count = 0
        self.timeout_count = 0

    async def connect(self) -> bool:
        """Initialize browser and navigate to the URL."""
        return await asyncio.to_thread(self._sync_connect)

    def _sync_connect(self) -> bool:
        """Synchronous part of connect for selenium."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Additional arguments for stability
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use eager page load strategy - don't wait for all resources
            chrome_options.page_load_strategy = 'eager'
            
            print(f"[WebScreen-Selenium] Initializing Chrome Driver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set explicit timeouts
            self.driver.set_page_load_timeout(20)  # 20 seconds max for page load
            self.driver.implicitly_wait(5)  # 5 seconds for element searches
            
            print(f"[WebScreen-Selenium] Navigating to {self.url}...")
            try:
                self.driver.get(self.url)
                print("[WebScreen-Selenium] Page loaded successfully!")
            except Exception as e:
                print(f"[WebScreen-Selenium] Page load timeout/error (continuing anyway): {str(e)[:100]}")
                # Page might still be usable even with timeout
            
            print("[WebScreen-Selenium] Page loaded, waiting for stabilization...")
            # Wait for page to stabilize
            time.sleep(15)
            
            # Look for and click the chatbot widget button
            print("[WebScreen-Selenium] Looking for chatbot trigger button...")
            chatbot_button_selectors = [
                # Specific to Tia chatbot - case-insensitive search for "need help" or "chat with tia"
                (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'need help')]"),
                (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'chat with tia')]"),
                (By.XPATH, "//*[contains(text(), 'Tia')]"),
                (By.XPATH, "//*[contains(text(), 'tia')]"),
                (By.CSS_SELECTOR, "button[class*='chat']"),
                (By.CSS_SELECTOR, "[class*='chat-widget']"),
            ]
            
            chatbot_opened = False
            for by, selector in chatbot_button_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"[WebScreen-Selenium] Found chatbot button with: {selector}")
                            elem.click()
                            chatbot_opened = True
                            print("[WebScreen-Selenium] Clicked chatbot button, waiting for chat to open...")
                            time.sleep(5)  # Wait for chat to open
                            break
                    if chatbot_opened:
                        break
                except Exception as e:
                    continue
            
            if not chatbot_opened:
                print("[WebScreen-Selenium] Warning: Could not find chatbot button, assuming chat is already visible")
            
            print("[WebScreen-Selenium] Connection successful!")
            return True
        except Exception as e:
            print(f"[WebScreen-Selenium] Connection failed: {e}")
            self.error_count += 1
            return False

    async def send_message(self, message: str) -> str:
        """Send a message to the chatbot and wait for the response."""
        return await asyncio.to_thread(self._sync_send_message, message)

    def _sync_send_message(self, message: str) -> str:
        """Synchronous part of send_message for selenium."""
        try:
            if not self.driver:
                if not self._sync_connect():
                    return "[Error: Unable to initialize browser]"

            # 1. Search for frames (iframes)
            self.driver.switch_to.default_content()
            frames = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"[WebScreen-Selenium] Found {len(frames)} iframes")
            
            # Helper to find input in current scope
            def find_input():
                input_selectors = [
                    # Tia chatbot specific
                    (By.CSS_SELECTOR, "input[placeholder='Type a message...']"),
                    (By.CSS_SELECTOR, "textarea[placeholder='Type a message...']"),
                    # Removing loose selectors that were matching main page forms
                    #(By.CSS_SELECTOR, "input[placeholder*='Type a message']"),
                    #(By.CSS_SELECTOR, "textarea[placeholder*='Type a message']"),
                    #(By.CSS_SELECTOR, "input[placeholder*='message']"),
                    #(By.CSS_SELECTOR, "textarea[placeholder*='message']"),
                    (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"), # More specific
                    (By.CSS_SELECTOR, ".chat-input textarea"),
                    (By.CSS_SELECTOR, ".chat-input input"),
                    (By.ID, "chat-input"),
                    # Generic fallback for inside iframes (only use if specific ones fail)
                    (By.CSS_SELECTOR, "textarea.textarea"),
                    (By.TAG_NAME, "textarea") 
                ]
                for by, selector in input_selectors:
                    try:
                        elements = self.driver.find_elements(by, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                # Verify it's not a read-only field (like a log)
                                if element.get_attribute("readonly"):
                                    continue
                                print(f"[WebScreen-Selenium] Found input with selector: {selector} (Tag: {element.tag_name})")
                                return element
                    except Exception as e:
                        continue
                return None

            input_field = None
            
            # OPTIMIZATION: Prioritize specific iframes based on ID or Name
            # The user identified that the chat is likely in 'avaamo_pdf_viewer' (index 3) or 'avaamoIframe' (index 4)
            # We will try to find these specific frames first.
            
            target_framenames = ["avaamoIframe", "avaamo_pdf_viewer", "avaamo_chat_window"]
            
            for name in target_framenames:
                if input_field: break
                try:
                    # Try to switch by name/id first
                    self.driver.switch_to.default_content()
                    # Try both switching by name/ID string and by finding element
                    try:
                        self.driver.switch_to.frame(name)
                        print(f"[WebScreen-Selenium] Switched to prioritized iframe by name: {name}")
                    except:
                        # Fallback to finding element if direct switch fails 
                        # (sometimes name attribute vs ID helps)
                        elem = self.driver.find_element(By.NAME, name) or self.driver.find_element(By.ID, name)
                        self.driver.switch_to.frame(elem)
                        print(f"[WebScreen-Selenium] Switched to prioritized iframe by element: {name}")

                    time.sleep(0.5)
                    input_field = find_input()
                    if input_field:
                        print(f"[WebScreen-Selenium] ✅ Found input in prioritized iframe: {name}")
                        break
                except:
                    pass
            
            # If not found in prioritized frames, try index 3 specifically as seen in logs - DIRECT JUMP
            if not input_field and len(frames) > 3:
                 try:
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame(3)
                    print(f"[WebScreen-Selenium] Switched to iframe index 3 (observed in logs)")
                    time.sleep(0.5)
                    input_field = find_input()
                    if input_field:
                         print(f"[WebScreen-Selenium] ✅ Found input in iframe index 3")
                 except Exception as e:
                     print(f"[WebScreen-Selenium] Failed checking iframe 3: {e}")
            
            # If still not found, search all frames
            if not input_field:
                # 1. Try cached iframe first
                if self.cached_iframe_index is not None and self.cached_iframe_index < len(frames):
                    try:
                        print(f"[WebScreen-Selenium] Checking CACHED iframe {self.cached_iframe_index}...")
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(self.cached_iframe_index)
                        time.sleep(0.5)
                        input_field = find_input()
                        if input_field:
                            print(f"[WebScreen-Selenium] ✅ Found input in CACHED iframe {self.cached_iframe_index}")
                    except Exception as e:
                        print(f"[WebScreen-Selenium] Cached iframe error: {e}")
                        self.cached_iframe_index = None # Reset cache on error

                # 2. If not found in cached iframe, search all frames
                if not input_field:
                    print(f"[WebScreen-Selenium] Searching {len(frames)} iframes...")
                    for idx, frame in enumerate(frames):
                        try:
                            # Skip if we already checked this index as cached (and failed)
                            if idx == self.cached_iframe_index:
                                continue
                                
                            print(f"[WebScreen-Selenium] Checking iframe {idx}/{len(frames)}...")
                            self.driver.switch_to.default_content()
                            self.driver.switch_to.frame(idx)  # Use index instead of element
                            time.sleep(0.5)  # Small delay for iframe to load
                            input_field = find_input()
                            if not input_field:
                                # Try broader search inside iframe if strict search fails
                                try:
                                    generic_inputs = self.driver.find_elements(By.TAG_NAME, "textarea") + \
                                                    self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                                    for inp in generic_inputs:
                                        if inp.is_displayed() and inp.is_enabled():
                                            input_field = inp
                                            print(f"[WebScreen-Selenium] Found generic input in iframe {idx}")
                                            break
                                except:
                                    pass
                                    
                            if input_field:
                                print(f"[WebScreen-Selenium] ✅ Found input in iframe {idx}")
                                self.cached_iframe_index = idx  # Save this index for next time
                                break
                            else:
                                print(f"[WebScreen-Selenium] No input in iframe {idx}")
                        except Exception as e:
                            print(f"[WebScreen-Selenium] Iframe {idx} error: {str(e)[:80]}")
                            continue
            
            if not input_field:
                # Removed broad search on main page to avoid false positives
                pass
            
            if not input_field:
                return "[Error: Chat input field not found]"

            # 2. Type message in the chat area and send with Enter key
            print(f"[WebScreen-Selenium] Typing message: {message[:50]}...")
            input_field.click()
            time.sleep(0.5)  # Wait for focus
            input_field.clear()  # Clear any existing text
            input_field.send_keys(message)
            time.sleep(0.5)  # Wait for message to be typed
            
            print("[WebScreen-Selenium] Sending message with Enter key...")
            input_field.send_keys(Keys.ENTER)
            print("[WebScreen-Selenium] ✅ Message sent with Enter key")

            # 3. Wait for response and extract it
            print("[WebScreen-Selenium] Waiting for response...")
            time.sleep(3)  # Give chatbot time to respond
            last_response = ""
            
            # Keywords to ignore (static footers/disclaimers and menu options)
            ignore_keywords = [
                "Air India Express Limited", 
                "wholly-owned subsidiary", 
                "Conditions of Carriage", 
                "Privacy Notice",
                "acknowledge and accept",
                "भाषा बदलें",  # Language change
                "Flight Canceled/Delayed",
                "I want to claim a refund",
                "Refund Status",
                "Check Flight Status",
                "Modify Booking Details",
                "Web Check-in",
                "Booking Status",
                "Appreciation/Complaint",
                "Skip to type a message",
                "You can select from the following"
            ]
            
            for _ in range(20): # Increased polling time
                # Search across current scope (iframe or main)
                response_selectors = [
                    (By.CSS_SELECTOR, ".bot-message"),
                    (By.CSS_SELECTOR, ".message-bot"),
                    (By.CSS_SELECTOR, ".tia-message"),
                    (By.CSS_SELECTOR, ".chat-bubble-received"),
                    (By.CSS_SELECTOR, "[class*='bot']"),
                    (By.CSS_SELECTOR, "[class*='bubble']"),
                    (By.TAG_NAME, "p"),
                    (By.TAG_NAME, "div")
                ]
                
                texts = []
                for by, selector in response_selectors:
                    try:
                        elements = self.driver.find_elements(by, selector)
                        for e in elements:
                            if e.is_displayed():
                                t = e.text.strip()
                                if t and t != message and len(t) > 5:
                                    # Filter out disclaimers and menu text
                                    if not any(kw in t for kw in ignore_keywords):
                                        # Only take responses that look like actual messages (contain "Tia" or are conversational)
                                        if "Tia" in t or "Welcome" in t or "help you" in t or len(t) < 500:
                                            texts.append(t)
                    except:
                        continue
                
                if texts:
                    # The actual latest message should be the last one in the filtered list
                    candidate = texts[-1]
                    # ignore very short strings or typing indicators
                    if len(candidate) > 2 and "..." not in candidate:
                        last_response = candidate
                        break
                time.sleep(1)

            if not last_response:
                # Fallback: Body text split with disclaimer filtering
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if message in body_text:
                        parts = body_text.split(message)
                        if len(parts) > 1:
                            # Look for content in the last part that isn't the disclaimer
                            potential_lines = [l.strip() for l in parts[-1].split("\n") if l.strip()]
                            for line in potential_lines:
                                if not any(kw in line for kw in ignore_keywords):
                                    last_response = line
                                    break
                except:
                    pass

            if not last_response:
                return "[Error: Unable to extract chatbot response]"

            print(f"[WebScreen-Selenium] Received: {last_response[:50]}...")
            self.success_count += 1
            return last_response

        except Exception as e:
            print(f"[WebScreen-Selenium] Error: {e}")
            self.error_count += 1
            return f"[Error: {str(e)}]"

    def reset_conversation(self):
        """Reset conversation state."""
        print("[WebScreen-Selenium] Resetting conversation (keeping chat open)...")
        # Don't refresh page as it closes the chat window
        # The chatbot maintains session, so we just continue
        pass

    async def close(self):
        """Clean up."""
        if self.driver:
            # Quit on thread to avoid blocking loop
            await asyncio.to_thread(self._sync_close)

    async def disconnect(self):
        """Disconnect from web chatbot (alias for close)."""
        await self.close()

    def _sync_close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
