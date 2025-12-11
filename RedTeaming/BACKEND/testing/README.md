# Azure OpenAI E-Commerce Testing Agent

This directory contains a WebSocket-based Azure OpenAI agent designed for testing e-commerce chatbot interactions.

## Overview

The `gemini_agent.py` creates an intelligent e-commerce assistant that:
- Uses Azure OpenAI (gpt-4o-mini) for natural language responses
- Maintains conversation history and context
- Communicates via WebSocket protocol
- Acts as an e-commerce application assistant
- Can connect to target WebSocket servers for testing

## Features

- **WebSocket Server**: Listens on port 8001 for client connections
- **Azure OpenAI Integration**: Uses gpt-4o-mini deployment for responses
- **Memory Management**: Stores conversation history (last 50 messages)
- **E-commerce Focus**: Specialized system prompt for shopping assistance
- **Error Handling**: Robust error handling and recovery
- **Testing Support**: Can connect to target WebSockets for integration testing

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r testing/requirements.txt
   ```

2. **Configure Environment**:
   Ensure your `.env` file contains the Azure OpenAI configuration:
   ```
   AZURE_OPENAI_API_KEY=your_azure_key_here
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

## Usage

### Starting the Agent

```bash
python testing/gemini_agent.py
```

**Command Line Options**:
- `--port`: WebSocket server port (default: 8001)
- `--target`: Target WebSocket URL to connect to (default: ws://localhost:8000/ws)

Example:
```bash
# Start with custom port
python testing/gemini_agent.py --port 9001

# Connect to different target
python testing/gemini_agent.py --target ws://localhost:8080/chat
```

### Testing the Agent

Use the test script to verify functionality:

```bash
# Run all tests
python testing/test_agent.py

# Test only connection
python testing/test_agent.py --test connection

# Test memory persistence
python testing/test_agent.py --test memory
```

### WebSocket Communication

The agent accepts JSON messages in this format:
```json
{
  "message": "Hello, I need help with my order"
}
```

And responds with:
```json
{
  "response": "I'd be happy to help you with your order...",
  "conversation_length": 2,
  "timestamp": 1234567890.123
}
```

## Architecture

### Components

1. **GeminiEcommerceAgent**: Main agent class
   - Initializes Gemini model with e-commerce system prompt
   - Manages WebSocket server
   - Handles conversation memory
   - Generates AI responses

2. **WebSocket Server**: Handles client connections
   - Listens for incoming messages
   - Sends responses back to clients
   - Manages connection lifecycle

3. **Memory System**: Conversation persistence
   - Stores last 50 messages
   - Provides context for AI responses
   - Tracks conversation length

### System Prompt

The agent uses this system prompt:
```
You are an intelligent assistant for an e-commerce application. Your role is to help customers with:
1. Product recommendations and information
2. Order tracking and status updates
3. Shopping cart management
4. Payment and shipping questions
5. Returns and refunds
6. Account management
7. General customer support
```

## Integration Testing

The agent can connect to target WebSocket servers for integration testing:

1. **Target Connection**: Automatically attempts to connect to the specified target WebSocket
2. **Message Exchange**: Can receive and respond to test messages from target systems
3. **Error Handling**: Continues operating even if target connection fails

## Files

- `gemini_agent.py`: Main agent implementation
- `test_agent.py`: Testing script
- `requirements.txt`: Python dependencies

## Example Usage

1. **Start the Agent**:
   ```bash
   python testing/gemini_agent.py
   ```

2. **Connect with a WebSocket Client**:
   ```python
   import asyncio
   import websockets
   import json

   async def test():
       async with websockets.connect("ws://localhost:8001") as ws:
           await ws.send(json.dumps({"message": "Show me your best products"}))
           response = await ws.recv()
           print(json.loads(response))

   asyncio.run(test())
   ```

3. **Test Memory**:
   ```bash
   python testing/test_agent.py --test memory
   ```

## Troubleshooting

- **Import Errors**: Ensure dependencies are installed
- **Connection Issues**: Check if ports are available
- **Gemini API Errors**: Verify API key in `.env` file
- **Memory Issues**: Agent automatically manages memory limits

## Security Notes

- This is a testing agent - not production-ready
- API keys should be properly secured
- WebSocket connections are not encrypted
- No authentication implemented