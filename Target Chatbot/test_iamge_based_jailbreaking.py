import asyncio
import json
import logging
import os
import glob
from datetime import datetime
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Middleware URL - Updated to 8001 as per the new architecture
MIDDLEWARE_URL = "ws://localhost:8001"

# Folder containing jailbreak images (place your images here)
IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jailbreak_images")

# Supported image extensions
IMAGE_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp")

# Default prompt sent with each image (can be customized per image via a .txt sidecar file)
DEFAULT_IMAGE_PROMPT = "Please explain what is in this image."


def get_image_files():
    """Collect all image files from the jailbreak_images folder, sorted by name."""
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(glob.glob(os.path.join(IMAGES_FOLDER, ext)))
    images.sort()
    return images


def get_prompt_for_image(image_path: str) -> str:
    base = os.path.splitext(image_path)[0]
    txt_path = base + ".txt"
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
            if prompt:
                return prompt
    return DEFAULT_IMAGE_PROMPT


async def test_automation_flow():
    if not os.path.isdir(IMAGES_FOLDER):
        logger.error(f"Images folder not found: {IMAGES_FOLDER}")
        return

    image_files = get_image_files()
    if not image_files:
        logger.error(f"No images found in {IMAGES_FOLDER}")
        return

    logger.info(f"Found {len(image_files)} image(s) in {IMAGES_FOLDER}")
    for img in image_files:
        logger.info(f"   - {os.path.basename(img)}")

    logger.info(f"Connecting to target chatbot middleware at {MIDDLEWARE_URL}...")

    try:
        async with websockets.connect(MIDDLEWARE_URL) as ws:
            logger.info("Connected to middleware.")

            # 1. Send initial greeting
            test_prompt_1 = {"prompt": "hi"}
            logger.info(f"Sending: {test_prompt_1['prompt']}")
            await ws.send(json.dumps(test_prompt_1))

            response_1 = await ws.recv()
            data_1 = json.loads(response_1)
            print(f"\n[CLIENT RECEIVED RESPONSE] {data_1.get('response')}\n")

            # 2. Loop through all images in the folder
            results = []
            for idx, image_path in enumerate(image_files, 1):
                image_name = os.path.basename(image_path)
                prompt = get_prompt_for_image(image_path)

                print(f"\n{'='*70}")
                print(f"  IMAGE {idx}/{len(image_files)}: {image_name}")
                print(f"  PROMPT: {prompt}")
                print(f"{'='*70}\n")

                logger.info(f"[{idx}/{len(image_files)}] Sending image: {image_name}")
                payload = {
                    "prompt": prompt,
                    "image_path": os.path.abspath(image_path)
                }
                await ws.send(json.dumps(payload))

                logger.info("Waiting for response...")
                response = await ws.recv()
                data = json.loads(response)

                if "error" in data:
                    logger.error(f"Error for {image_name}: {data['error']}")
                    results.append({
                        "image": image_name,
                        "prompt": prompt,
                        "response": None,
                        "error": data["error"],
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    response_text = data.get("response", "")
                    print(f"\n[RESPONSE for {image_name}]\n{response_text}\n")
                    results.append({
                        "image": image_name,
                        "prompt": prompt,
                        "response": response_text,
                        "error": None,
                        "timestamp": datetime.now().isoformat()
                    })

                # Small delay between images to avoid overwhelming the UI
                await asyncio.sleep(2)

            # 3. Save results to JSON
            results_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f"image_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump({
                    "test_run": datetime.now().isoformat(),
                    "total_images": len(image_files),
                    "results": results
                }, f, indent=2, ensure_ascii=False)

            print(f"\n{'='*70}")
            print(f"  TEST COMPLETE: {len(results)} image(s) processed")
            print(f"  Results saved to: {results_file}")
            print(f"{'='*70}\n")

            logger.info("Test flow completed. Closing connection.")

    except Exception as e:
        logger.error(f"Connection failed: {e}")
        print("Tip: Make sure the middleware is running (python BACKEND/middlewares/custom_chatbot_middleware.py)")

if __name__ == "__main__":
    asyncio.run(test_automation_flow())