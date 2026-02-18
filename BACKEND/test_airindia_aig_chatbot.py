"""
Simple test script to verify Air India Ai.g chatbot automation
Opens chatbot, sends "hi", and displays response
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.web_screen_target import WebScreenTarget
from selenium.webdriver.common.by import By


async def test_chatbot():
    """Test chatbot by sending hi and getting response"""

    print("="*80)
    print("🧪 TESTING AIR INDIA AI.G CHATBOT")
    print("="*80)
    print("Target: https://www.airindia.com/")
    print("="*80 + "\n")

    # Initialize web target
    target_url = "https://www.airindia.com/"
    headless = False  # Show browser for debugging

    print(f"Initializing WebScreenTarget...")
    print(f"  - URL: {target_url}")
    print(f"  - Headless: {headless}\n")

    web_target = WebScreenTarget(
        url=target_url,
        headless=headless
    )

    try:
        # Step 1: Connect to chatbot
        print("🔗 Step 1: Connecting to Air India Ai.g chatbot...")
        print("           This will:")
        print("           1. Open Chrome browser")
        print("           2. Navigate to Air India website")
        print("           3. Find and click 'Chat with Ai.g' button")
        print("           4. Open Ai.g chatbot\n")

        success = await web_target.connect()

        if not success:
            print("❌ Failed to connect to chatbot")
            print("   Check if:")
            print("   - Chrome is installed")
            print("   - Website is accessible")
            print("   - Selenium is installed in venv")
            return

        print("✅ Connected successfully!\n")

        # Step 2: Send "hi" message
        print("💬 Step 2: Sending message 'hi'...")
        
        # Locate and click the chatbot button
        print("🔍 Locating chatbot button...")
        try:
            # Try specific Ai.g button with ID "ask-aig"
            # We use a wait to ensure it's present
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(web_target.driver, 10)
            chatbot_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ask-aig, .floating-chat-bot-icon, #avaamo_chat_button")))
            
            # Use JavaScript click to bypass "element not interactable" or "zero size" errors
            print("🚀 Using JavaScript click to start conversation...")
            web_target.driver.execute_script("arguments[0].scrollIntoView(true);", chatbot_button)
            web_target.driver.execute_script("arguments[0].click();", chatbot_button)
            
            print("✅ Chatbot button clicked via JS!\n")
        except Exception as e:
            print(f"⚠️ JS Click failed or button already open: {e}")

        # Wait for the chat to load and switch to iframe if necessary
        print("⏳ Waiting for chat window and switching to iframe...")
        await asyncio.sleep(5)
        
        # Try to find the correct iframe by checking all frames
        frames = web_target.driver.find_elements(By.TAG_NAME, "iframe")
        found_frame = False
        print(f"📊 Found {len(frames)} iframes on the page.")
        
        for idx, frame in enumerate(frames):
            try:
                web_target.driver.switch_to.default_content()
                web_target.driver.switch_to.frame(frame)
                
                # Check for ANY input that might be the chat input
                # Avaamo often uses: textarea[placeholder='Type your question here...']
                # or just a generic textarea
                inputs = web_target.driver.find_elements(By.TAG_NAME, "textarea") + \
                         web_target.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                
                for inp in inputs:
                    ph = inp.get_attribute("placeholder") or ""
                    cls = inp.get_attribute("class") or ""
                    
                    # Print debug info about found inputs
                    # print(f"   [Frame {idx}] Input found: Placeholder='{ph}', Class='{cls}'")
                    
                    if "question" in ph.lower() or "type" in ph.lower() or "avaamo" in cls.lower():
                        print(f"✅ Found and switched to chatbot iframe (Index: {idx}) - Matched input: {ph}")
                        found_frame = True
                        break
                
                if found_frame:
                    break
            except Exception as e:
                # print(f"   [Frame {idx}] Error checking: {e}")
                continue
        
        if not found_frame:
            # Fallback: Maybe it's the specific specific "avaamoIframe" 
            try:
                web_target.driver.switch_to.default_content()
                iframe = web_target.driver.find_element(By.CSS_SELECTOR, "iframe[name='avaamoIframe'], iframe.avaamo__iframe")
                web_target.driver.switch_to.frame(iframe)
                print("✅ Found and switched to 'avaamoIframe' by name/class")
                found_frame = True
            except:
                web_target.driver.switch_to.default_content()
                print("ℹ️ No specific iframe found for input, staying in main content")

        # Find the chat input field
        print("🔍 Finding chat input field...")
        
        # Try finding input in the current scope
        chat_inputs = web_target.driver.find_elements(By.TAG_NAME, "textarea") + \
                      web_target.driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='Type'], input[placeholder*='type']")
        
        chat_input = None
        for inp in chat_inputs:
            ph = inp.get_attribute("placeholder") or ""
            if "question" in ph.lower() or "type" in ph.lower():
                chat_input = inp
                print(f"✅ Input field selected: placeholder='{ph}'")
                break
        
        if not chat_input:
            print("⚠️ Could not verify exact placeholder, trying the first visible textarea...")
            visible_tas = [ta for ta in web_target.driver.find_elements(By.TAG_NAME, "textarea") if ta.is_displayed()]
            if visible_tas:
                chat_input = visible_tas[0]
                print("✅ Selected first visible textarea")
            else:
                # Last resort: generic search
                chat_input = web_target.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
                print("⚠️ Selected generic input")

        # Type and send the message
        print("💬 Typing and sending message 'hi'...")
        chat_input.click()
        chat_input.clear()
        chat_input.send_keys("hi")
        time.sleep(0.5)
        chat_input.send_keys(Keys.ENTER)
        print("✅ Message sent!\n")

        # Wait for the response to appear
        print("⏳ Waiting for chatbot response...")
        await asyncio.sleep(5)

        # Locate and log the chatbot response
        print("🔍 Locating chatbot response...")
        try:
            # We'll try to find ANY elements with text first to see what's there
            print("⏳ Waiting for messages to appear...")
            
            # Very broad selector to find any bubble-like element
            # Avaamo: .desc is the inner text, .receiver is the bot's bubble
            response_selector = ".desc, .message-content, .receiver, [class*='message']"
            
            wait = WebDriverWait(web_target.driver, 20)
            
            # Wait for any of these to be present
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, response_selector)))
            
            print(f"📊 Elements found: {len(elements)}")
            
            # Let's log everything we found to see what's happening
            all_messages = []
            for i, el in enumerate(elements):
                try:
                    txt = el.text.strip()
                    if txt:
                        # Find out if it's bot or user
                        p_class = el.get_attribute("class") or ""
                        # Walk up to find 'receiver' or 'sender'
                        try:
                            parent = el.find_element(By.XPATH, "./parent::*")
                            p_class += " " + (parent.get_attribute("class") or "")
                        except: pass
                        
                        msg_type = "🤖 BOT" if "receiver" in p_class else "👤 USER"
                        all_messages.append(f"[{msg_type}] {txt}")
                except:
                    continue

            # Log all read items
            print("\n📜 Conversation History detected:")
            for msg in all_messages:
                print(f"  {msg}")

            # Extract the actual response (any message that is not 'hi')
            # Since Avaamo classes might be tricky, let's just grab the last message that isn't our 'hi'
            # We filter out empty strings and exact matches of our input
            responses = [m.split("] ", 1)[1] for m in all_messages if len(m.split("] ", 1)) > 1]
            valid_responses = [r for r in responses if r.strip().lower() != "hi"]
            
            if valid_responses:
                response = valid_responses[-1]
                print(f"\n✅ SUCCESS: Captured Response: {response}")
            else:
                # If we still can't find it, try a very raw dump of text visible in the chat area
                try:
                    chat_container = web_target.driver.find_element(By.CSS_SELECTOR, ".conversation-container, .message-list, [class*='chat-window'], [class*='conversation']")
                    raw_text = chat_container.text
                    print(f"\n⚠️ Fallback: Raw Chat Text:\n{raw_text}")
                    response = raw_text
                except:
                    print("⚠️ No BOT messages identified in the list and fallback failed.")
                    response = ""

        except Exception as e:
            print(f"⚠️ Error during response capture: {e}")
            # Debug: print page source snippet to see what's actually there
            try:
                print("\n🔍 DEBUG: First 500 chars of iframe source:")
                print(web_target.driver.page_source[:500])
            except: pass
            response = ""

        if "[Error" in response or "Error:" in response:
            print("⚠️ Response contains error!")
            print("   Check the browser window to see what happened.")
        else:
            print("✅ Successfully received response from Ai.g chatbot!")

        # Keep browser open for inspection
        print("\n⏸️  Keeping browser open for 15 seconds for visual inspection...")
        await asyncio.sleep(15)

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("\nKeeping browser open for 10 seconds so you can inspect...")
        await asyncio.sleep(10)

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            # await web_target.disconnect()
            print("✅ Browser closed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
        print("✅ Test complete!")


if __name__ == "__main__":
    print("\n🚀 Starting Chatbot Test...\n")
    try:
        asyncio.run(test_chatbot())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()