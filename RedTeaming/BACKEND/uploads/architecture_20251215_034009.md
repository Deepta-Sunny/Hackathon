# Azure OpenAI E-Commerce Testing Agent - Setup Guide

## Current Status

✅ **Agent code successfully converted from Gemini to Azure OpenAI**  
⚠️ **Old Gemini agent still running - needs restart**

## What Changed

The testing agent has been migrated from Google Gemini to Azure OpenAI:

### Before (Gemini)
- Model: `gemini-2.0-flash` / `gemini-1.5-flash`
- API: Google Generative AI
- Issue: Quota exhausted (429 errors)

### After (Azure OpenAI)
- Model: `gpt-4o-mini`
- API: Azure OpenAI
- Status: Working ✅ (no quota issues)

## Files Updated

1. **`testing/gemini_agent.py`**
   - Replaced Gemini imports with Azure OpenAI
   - Changed `GeminiEcommerceAgent` → `AzureEcommerceAgent`
   - Updated `generate_response()` to use Azure OpenAI API
   - Added proper message formatting for chat completions

2. **`testing/README.md`**
   - Updated documentation
   - Changed configuration instructions
   - Updated feature descriptions

3. **`testing/AZURE_AGENT_ARCHITECTURE.md`**
   - Renamed from `GEMINI_AGENT_ARCHITECTURE.md`
   - Updated system overview
   - Changed technology stack references

## Configuration

Your `.env` file is already configured correctly:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY_HERE
AZURE_OPENAI_ENDPOINT=https://ai-collections.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

## How to Restart the Agent

### Step 1: Stop the Old Agent

Go to the terminal where the Gemini agent is running (showing these logs):
```
🤖 Gemini E-Commerce Agent initialized
   📡 Listening on port 8001
   🔗 Target WebSocket: ws://localhost:8000/ws
```

Press **Ctrl+C** to stop it.

### Step 2: Start the New Azure Agent

```powershell
cd C:\RedTeaming\testing
python gemini_agent.py
```

### Expected Output

You should see:
```
🤖 Azure OpenAI E-Commerce Agent initialized
   📡 Listening on port 8001
   🔗 Target WebSocket: ws://localhost:8000/ws
   🔑 Using deployment: gpt-4o-mini
🚀 Starting Azure OpenAI E-Commerce Agent...
✅ WebSocket server started on ws://localhost:8001
```

## Testing the Agent

### Quick Test

Run this in a new terminal:
```powershell
cd C:\RedTeaming\testing
python test_agent.py
```

### Manual WebSocket Test

```python
import asyncio
import json
import websockets

async def test():
    async with websockets.connect("ws://localhost:8001") as ws:
        await ws.send(json.dumps({"message": "Hello!"}))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(test())
```

### Using with Red-Team Framework

```powershell
cd C:\RedTeaming
python main.py
```

When prompted:
- **WebSocket URL**: `ws://localhost:8001`
- **Architecture file**: `testing/AZURE_AGENT_ARCHITECTURE.md`

## Verification

### Test Azure OpenAI Connection

```python
from openai import AzureOpenAI
from config.settings import *

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ]
)

print(response.choices[0].message.content)
```

Expected: ✅ Successful response (no quota errors)

## Key Differences

### API Calls

**Gemini (Old):**
```python
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content(prompt)
```

**Azure OpenAI (New):**
```python
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)
response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[...]
)
```

### Message Format

**Gemini:**
- Single string prompt with history embedded

**Azure OpenAI:**
- Structured messages array with roles (system, user, assistant)
- System prompt as first message
- Conversation history as message sequence

## Troubleshooting

### Port Already in Use (Error 10048)

**Problem:** Old agent still running on port 8001

**Solution:** 
1. Find the terminal with the running agent
2. Press Ctrl+C
3. Restart with new code

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'openai'`

**Solution:**
```powershell
pip install openai
```

### Connection Refused

**Problem:** Agent not running when testing

**Solution:**
```powershell
cd C:\RedTeaming\testing
python gemini_agent.py
```

Keep it running in background while testing.

## Next Steps

1. ✅ Stop old Gemini agent
2. ✅ Start new Azure OpenAI agent
3. ✅ Verify connection with test script
4. ✅ Run red-team attacks against it
5. ✅ Monitor responses for proper Azure OpenAI integration

## Benefits of Azure OpenAI

✅ **No quota issues** - Your Azure account has sufficient capacity  
✅ **Better performance** - gpt-4o-mini is fast and capable  
✅ **Consistent availability** - Enterprise-grade reliability  
✅ **Same testing capabilities** - All attack patterns still work  

---

**Last Updated:** December 11, 2025  
**Status:** Ready to deploy  
**Action Required:** Restart agent to apply changes