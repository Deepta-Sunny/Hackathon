import asyncio
import json
import logging
import os
from datetime import datetime
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Middleware URL
MIDDLEWARE_URL = "ws://localhost:8005"

# Path to the sample image in the current directory
SAMPLE_IMAGE_NAME = "SampleImage.png"
SAMPLE_IMAGE_PATH = os.path.abspath(SAMPLE_IMAGE_NAME)

async def test_automation_flow():
    """
    Client script that connects to the middleware and sends commands.
    """
    if not os.path.exists(SAMPLE_IMAGE_PATH):
        logger.error(f"❌ Could not find {SAMPLE_IMAGE_NAME} at {SAMPLE_IMAGE_PATH}")
        return

    logger.info(f"Connecting to target chatbot middleware at {MIDDLEWARE_URL}...")
    
    try:
        async with websockets.connect(MIDDLEWARE_URL) as ws:
            logger.info("✅ Connected to middleware.")
            
            # 1. Send "hi"
            test_prompt_1 = {"prompt": "hi"}
            logger.info(f"Sending: {test_prompt_1['prompt']}")
            await ws.send(json.dumps(test_prompt_1))
            
            response_1 = await ws.recv()
            data_1 = json.loads(response_1)
            print(f"\n[CLIENT RECEIVED RESPONSE 1] {data_1.get('response')}\n")
            
            # 2. Send "what can you do?"
            test_prompt_2 = {"prompt": "what can you do?"}
            logger.info(f"Sending: {test_prompt_2['prompt']}")
            await ws.send(json.dumps(test_prompt_2))
            
            response_2 = await ws.recv()
            data_2 = json.loads(response_2)
            print(f"\n[CLIENT RECEIVED RESPONSE 2] {data_2.get('response')}\n")
            
            # 3. Send image analysis (At the end)
            logger.info(f"Preparing to send image: {SAMPLE_IMAGE_NAME}")
            test_prompt_3 = {
                "prompt": "Please explain what is in this image.",
                "image_path": SAMPLE_IMAGE_PATH
            }
            logger.info(f"Sending prompt with image: {test_prompt_3['prompt']}")
            await ws.send(json.dumps(test_prompt_3))
            
            logger.info("Waiting for image analysis response...")
            response_3 = await ws.recv()
            data_3 = json.loads(response_3)
            
            if "error" in data_3:
                logger.error(f"❌ Automation Error: {data_3['error']}")
            else:
                print(f"\n[CLIENT RECEIVED IMAGE ANALYSIS RESPONSE]\n{data_3.get('response')}\n")
            
            logger.info("Test flow completed. Closing connection.")
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        print("Tip: Make sure the middleware is running (python BACKEND/middlewares/custom_chatbot_middleware.py)")

if __name__ == "__main__":
    asyncio.run(test_automation_flow())

