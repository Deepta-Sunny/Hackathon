"""
Simple test script to verify Tia chatbot interaction
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def test_tia_chatbot():
    print("="*80)
    print("🧪 Testing Tia Chatbot Interaction")
    print("="*80)
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.page_load_strategy = 'eager'
    
    print("\n[1] Initializing Chrome Driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)
    
    try:
        # Navigate to website
        print("[2] Navigating to Air India Express...")
        url = "https://www.airindiaexpress.com/"
        try:
            driver.get(url)
            print("    ✓ Page loaded")
        except Exception as e:
            print(f"    ⚠ Timeout (continuing): {str(e)[:80]}")
        
        time.sleep(10)
        
        # Look for chatbot button
        print("[3] Looking for Tia chatbot button...")
        chatbot_opened = False
        
        selectors = [
            (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'need help')]"),
            (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'chat with tia')]"),
            (By.XPATH, "//*[contains(text(), 'Tia')]"),
            (By.XPATH, "//*[contains(text(), 'tia')]"),
            (By.CSS_SELECTOR, "button[class*='chat']"),
            (By.CSS_SELECTOR, "[class*='chat-widget']"),
        ]
        
        for by, selector in selectors:
            try:
                elements = driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed():
                        print(f"    ✓ Found button: {selector[:50]}")
                        elem.click()
                        chatbot_opened = True
                        time.sleep(5)
                        break
                if chatbot_opened:
                    break
            except:
                continue
        
        if not chatbot_opened:
            print("    ⚠ Chatbot button not found, assuming chat is visible")
        
        # Find input field
        print("[4] Looking for chat input field...")
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"    Found {len(frames)} iframes")
        
        input_field = None
        input_selectors = [
            (By.CSS_SELECTOR, "input[placeholder*='message']"),
            (By.CSS_SELECTOR, "textarea[placeholder*='message']"),
            (By.CSS_SELECTOR, "input[placeholder*='Type']"),
            (By.CSS_SELECTOR, "textarea[placeholder*='Type']"),
            (By.TAG_NAME, "textarea"),
            (By.TAG_NAME, "input")
        ]
        
        # Search in main document
        for by, selector in input_selectors:
            try:
                elem = driver.find_element(by, selector)
                if elem.is_displayed():
                    input_field = elem
                    print(f"    ✓ Found input: {selector}")
                    break
            except:
                continue
        
        # Search in iframes
        if not input_field:
            for idx, frame in enumerate(frames):
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                for by, selector in input_selectors:
                    try:
                        elem = driver.find_element(by, selector)
                        if elem.is_displayed():
                            input_field = elem
                            print(f"    ✓ Found input in iframe {idx}: {selector}")
                            break
                    except:
                        continue
                if input_field:
                    break
        
        if not input_field:
            print("    ✗ Input field not found!")
            return
        
        # Send message
        print("[5] Sending message: 'hi'")
        input_field.click()
        time.sleep(1)
        input_field.send_keys("hi")
        
        # Find and click send button
        print("[6] Looking for send button...")
        send_selectors = [
            (By.XPATH, "//button[.//svg]"),
            (By.CSS_SELECTOR, "button[aria-label*='send']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(@class, 'send')]"),
        ]
        
        sent = False
        for by, selector in send_selectors:
            try:
                btn = driver.find_element(by, selector)
                if btn.is_displayed():
                    btn.click()
                    sent = True
                    print(f"    ✓ Clicked send button: {selector[:50]}")
                    break
            except:
                continue
        
        if not sent:
            print("    Using Enter key")
            input_field.send_keys(Keys.ENTER)
        
        # Wait for response
        print("[7] Waiting for response...")
        time.sleep(5)
        
        # Extract response
        ignore_keywords = [
            "Air India Express Limited", 
            "wholly-owned subsidiary", 
            "Conditions of Carriage"
        ]
        
        response_selectors = [
            (By.CSS_SELECTOR, ".bot-message"),
            (By.CSS_SELECTOR, ".message-bot"),
            (By.CSS_SELECTOR, "[class*='bot']"),
            (By.CSS_SELECTOR, "[class*='assistant']"),
            (By.TAG_NAME, "p"),
            (By.TAG_NAME, "div")
        ]
        
        responses = []
        for by, selector in response_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for e in elements:
                    if e.is_displayed():
                        text = e.text.strip()
                        if text and text != "hi" and len(text) > 5:
                            if not any(kw in text for kw in ignore_keywords):
                                responses.append(text)
            except:
                continue
        
        print("\n" + "="*80)
        print("📝 EXTRACTED RESPONSES:")
        print("="*80)
        if responses:
            # Show unique responses
            unique = list(set(responses))
            for i, resp in enumerate(unique[:5], 1):
                print(f"\n[Response {i}]:")
                print(resp[:200])
                if len(resp) > 200:
                    print("...")
        else:
            print("No responses found!")
            print("\nFull page text (first 500 chars):")
            print(driver.find_element(By.TAG_NAME, "body").text[:500])
        
        print("\n" + "="*80)
        print("Keeping browser open for 30 seconds for manual inspection...")
        time.sleep(30)
        
    finally:
        driver.quit()
        print("\n✓ Test complete!")

if __name__ == "__main__":
    test_tia_chatbot()
