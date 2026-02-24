"""
Simple test script to verify Air India Ai.g chatbot automation
Opens chatbot, sends "hi", and displays response
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.web_screen_target import WebScreenTarget
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
            return

        print("✅ Connected successfully!\n")

        # Step 1.5: Dismiss cookie consent popup if present
        print("🍪 Step 1.5a: Dismissing cookie consent popup if present...")
        try:
            cookie_btn = WebDriverWait(web_target.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            print("✅ Cookie consent dismissed!")
            await asyncio.sleep(1)
        except Exception:
            print("ℹ️  No cookie popup found, continuing...")

        # Step 1.5b: Click chatbot icon using JS click (bypasses interception)
        # HARDCODED: chatbot icon id="ask-aig" in main document
        print("🖱️  Step 1.5b: Clicking chatbot icon (id='ask-aig')...")
        try:
            chatbot_icon = WebDriverWait(web_target.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ask-aig"))
            )
            web_target.driver.execute_script("arguments[0].click();", chatbot_icon)
            print("✅ Clicked chatbot icon!")
            print("⏳ Waiting for chat window to load (3 seconds)...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️  Could not click chatbot icon: {e}")

        # Step 2: Locate input field
        # HARDCODED: inputChat is in the main document (no iframe switch needed)
        print("\n💬 Step 2: Locating input field (id='inputChat') in main document...")
        input_field = None
        try:
            input_field = WebDriverWait(web_target.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "inputChat"))
            )
            print("✅ Found 'inputChat'!")
        except Exception as e:
            print(f"❌ Could not find input field: {e}")
            return

        # Step 3: Type and send message
        print("\n💬 Step 3: Typing message 'hi' and sending...")
        try:
            input_field.click()
            time.sleep(0.5)
            input_field.clear()
            input_field.send_keys("hi")
            time.sleep(0.5)
            input_field.send_keys(Keys.RETURN)
            print("✅ Message sent!")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return
        
        # Step 4: Wait for response
        print("⏳ Step 4: Waiting for chatbot response (5 seconds)...")
        await asyncio.sleep(5)
        
        # Step 5: Extract response
        # HARDCODED: bot responses are in <p class="child"> inside .bot-chat-content
        print("🔍 Step 5: Extracting response from chat...")
        response = ""
        
        try:
            # Wait for at least one bot response to appear
            WebDriverWait(web_target.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".bot-chat-content p.child"))
            )
            
            # Get all bot response paragraphs and take the last one
            bot_messages = web_target.driver.find_elements(By.CSS_SELECTOR, ".bot-chat-content p.child")
            if bot_messages:
                response = bot_messages[-1].text.strip()
                print(f"✅ Found {len(bot_messages)} bot message(s). Latest: '{response[:100]}'")
            else:
                response = "[Error: No bot messages found]"
        except Exception as e:
            response = f"[Error: {str(e)}]"
            print(f"❌ Error extracting response: {e}")
        
        # Step 6: Display first response
        print("\n" + "="*80)
        print("📥 RESPONSE #1 FROM AI.G: ")
        print("="*80)
        print(response)
        print("="*80 + "\n")

        # Step 7: Interactive chat loop — type Q to quit
        print("💬 Interactive Chat Mode (type 'Q' to quit)\n")
        msg_count = 1
        prev_msg_count = len(bot_messages)

        while True:
            # Get user input from terminal
            user_input = await asyncio.to_thread(input, "You: ")
            
            if user_input.strip().upper() == "Q":
                print("\n👋 Exiting chat. Goodbye!")
                break

            if not user_input.strip():
                continue

            # Send the message to chatbot
            try:
                input_field = WebDriverWait(web_target.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "inputChat"))
                )
                input_field.click()
                time.sleep(0.3)
                input_field.clear()
                input_field.send_keys(user_input.strip())
                time.sleep(0.3)
                input_field.send_keys(Keys.RETURN)
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                continue

            # Wait for a new bot response to appear
            try:
                WebDriverWait(web_target.driver, 15).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, ".bot-chat-content p.child")) > prev_msg_count
                )
                all_bot_messages = web_target.driver.find_elements(By.CSS_SELECTOR, ".bot-chat-content p.child")
                new_response = all_bot_messages[-1].text.strip()
                prev_msg_count = len(all_bot_messages)
                msg_count += 1
                print(f"\nAi.g: {new_response}\n")
            except Exception as e:
                print(f"⚠️  Could not get response: {e}\n")


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
        print("\n🧹 Cleanup...")
        print("ℹ️  Browser will remain open for manual inspection")
        print("   Close the browser window manually when done")
        print("✅ Test complete!")

        # Keep browser open - DO NOT close it automatically
        # await web_target.disconnect()  # Commented out to keep browser open


if __name__ == "__main__":
    print("\n🚀 Starting Chatbot Test...\n")
    try:
        asyncio.run(test_chatbot())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        