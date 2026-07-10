"""
Configuration settings for the Target Chatbot backend.
Loads from .env file in the backend directory.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory (same folder as this config package)
_backend_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=_backend_dir / ".env")

# =========================================================================
# AZURE OPENAI CONFIGURATION
# =========================================================================
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
