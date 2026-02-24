"""
Simple test script to verify Air India Tia chatbot automation
Opens chatbot, sends "hi", and displays response
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.web_screen_target import WebScreenTarget


async def test_chatbot():
    """Test chatbot by sending hi and getting response"""
    
    print("="*80)
    print("🧪 TESTING AIR INDIA TIA CHATBOT")
    print("="*80)
    print("Target: https://www.airindiaexpress.com/")
    print("="*80 + "\n")
    
    # Initialize web target
    target_url = "https://www.airindiaexpress.com/"
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
        print("🔗 Step 1: Connecting to Air India chatbot...")
        print("           This will:")
        print("           1. Open Chrome browser")
        print("           2. Navigate to Air India Express")
        print("           3. Find and click 'Need Help' button")
        print("           4. Open Tia chatbot\n")
        
        success = await web_target.connect()
        
        if not success:
            print("❌ Failed to connect to chatbot")
            print("   Check if:")
            print("   - Chrome is installed")
            print("   - Website is accessible")
            print("   - Selenium is installed in venv")
            return
        
        print("✅ Connected successfully!\n")
        
        # DEBUG: Log all iframe details
        # print("🔍 Debugging: Listing all iframes...")
        try:
            from selenium.webdriver.common.by import By
            frames = web_target.driver.find_elements(By.TAG_NAME, "iframe")
            # print(f"   Found {len(frames)} iframes:")
            for idx, frame in enumerate(frames):
                f_id = frame.get_attribute("id") or "N/A"
                f_name = frame.get_attribute("name") or "N/A"
                f_src = frame.get_attribute("src") or "N/A"
                f_class = frame.get_attribute("class") or "N/A"
                # print(f"   [{idx}] ID: {f_id} | Name: {f_name} | Class: {f_class}")
                # print(f"       Src: {f_src[:100]}...") # Truncate src
        except Exception as e:
            print(f"   ⚠️ Could not list frames: {e}")
        print("-" * 50 + "\n")

        # Step 2: Send "hi" message
        print("💬 Step 2: Sending message 'hi'...")
        # print("           This will:")
        # print("           1. Find the chat input field")
        # print("           2. Type 'hi' in the input")
        # print("           3. Click Send button (or press Enter)")
        # print("           4. Wait for Tia's response\n")
        
        response = await web_target.send_message("hi")
        
        # Step 3: Display response
        # print("\n" + "="*80)
        print("📥 RESPONSE FROM TIA: ")
        # print("="*80)
        print(response)
        # print("="*80 + "\n")
        
        if "[Error" in response or "Error:" in response:
            print("⚠️ Response contains error!")
            print("   Check the browser window to see what happened.")
        else:
            print("✅ Successfully received response from Tia chatbot!")
            # print(f"   Response length: {len(response)} characters")

        # Step 4: Test cache with second message
        print("\n💬 Step 3: Sending second message 'What are your flight routes?' to test cache...")
        response2 = await web_target.send_message("What are your flight routes?")
        # print("\n" + "="*80)
        print("📥 RESPONSE 2 FROM TIA:")
        # print("="*80)
        print(response2)
        # print("="*80 + "\n")
        
        # Keep browser open for inspection
        print("\n⏸️  Keeping browser open for 15 seconds for visual inspection...")
        # print("   You can manually interact with the chatbot if needed.")
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
            await web_target.disconnect()
            print("✅ Browser closed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
        print("✅ Test complete!")


if __name__ == "__main__":
    print("\n🚀 Starting Chatbot Test...\n")
    # print("⚠️  IMPORTANT: Make sure you're using the virtual environment!")
    # print("   Run: .\\venv\\Scripts\\python.exe testing_chat.py\n")
    
    try:
        asyncio.run(test_chatbot())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()