import base64
import os
import sys
from pathlib import Path
from openai import AzureOpenAI

# Add backend directory to path to resolve local config
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from backend.config.settings import (
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_DEPLOYMENT,
        AZURE_OPENAI_API_VERSION
    )
except ImportError:
    print("❌ Could not import settings. Please ensure this script is in 'Target Chatbot' directory.")
    sys.exit(1)

# Initialize Azure OpenAI client using existing chatbot config
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Image path provided by user
IMAGE_PATH = "SampleImage.png"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_image_input():
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: {IMAGE_PATH} not found!")
        return

    print(f"🔄 Encoding image: {IMAGE_PATH}...")
    base64_image = encode_image(IMAGE_PATH)

    print(f"🚀 Sending multimodal request to {AZURE_OPENAI_DEPLOYMENT} (gpt-4o-mini)...")
    
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the image in detail. What objects do you see?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        print("\n✅ [MODEL RESPONSE]:")
        print("-" * 50)
        print(response.choices[0].message.content)
        print("-" * 50)

    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    test_image_input()
