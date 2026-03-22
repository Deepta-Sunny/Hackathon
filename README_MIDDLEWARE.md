# Custom Chatbot Selenium Middleware

This middleware acts as an automation bridge between the **Red Teaming Orchestrator** and the **Target Chatbot's React UI**. It exposes a WebSocket interface that translates text and image-based prompts into browser actions using Selenium.

---

## Architecture Overview

The system operates in three layers:
1. **The UI (Frontend)**: React application running at `http://localhost:3000`.
2. **The Middleware**: Python Selenium engine acting as a WebSocket server on `ws://localhost:8001`.
3. **The Test Client**: User scripts that send commands to the middleware.

---

## Design Evolution: "Silent" Image Upload

A key design challenge was handling image uploads without triggering the operating system's native file picker (which blocks automation).

### How it's implemented:
1. **WebSocket Protocol**: The middleware accepts a JSON payload containing `prompt` and `image_path`.
2. **Hidden Input Manipulation**:
   - The React UI uses a standard `<input type="file" id="image-input" style="display: none;">`.
   - The middleware uses Selenium `execute_script` to temporarily set the input to `display: block`.
3. **Path Injection**: It uses `file_input.send_keys(image_path)` to inject the absolute file path directly into the browser's upload buffer.
4. **State Synchronization**: The middleware waits for the UI to render the `preview-thumb` element before attempting to click the "Send" button. This ensures the frontend state has fully processed the file.

---

## Test Execution Detail: `test_iamge_based_jailbreaking.py`

This script demonstrates the end-to-end automation flow:

1. **Path Resolution**: It automatically detects the absolute path of `SampleImage.png` in its local directory.
2. **Protocol Handshake**: Connects to the middleware on port `8001`.
3. **Sequential Automation**:
   - **Step 1 & 2**: Sends standard text prompts to verify the connection and response extraction logic.
   - **Step 3 (Image Attack)**: Sends a JSON object:
     ```json
     {
       "prompt": "Please explain what is in this image.",
       "image_path": "C:\\path\\to\\SampleImage.png"
     }
     ```
4. **Response Polling**: The script waits (awaits `ws.recv()`) while the middleware drives the browser, detects the bot's typing indicator, extracts the text from the generated `bot-bubble`, and returns the final response string.

---

## Startup Sequence
To run the full stack, use:
```powershell
.\MasterScript_CustomChatbot.ps1
```
This script handles the port clearance, environment activation, and window management for all three layers automatically.
