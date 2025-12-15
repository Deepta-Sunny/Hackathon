"""
Test Azure OpenAI connection and credentials
"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def test_azure_connection():
    """Test Azure OpenAI API connection"""
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    print("=" * 70)
    print("Testing Azure OpenAI Configuration")
    print("=" * 70)
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Version: {api_version}")
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT SET'}")
    print("=" * 70)
    
    if not all([endpoint, api_key, deployment, api_version]):
        print("❌ ERROR: Missing required configuration")
        return False
    
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Connection successful!' if you can read this."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        print("\n🔄 Attempting connection...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ SUCCESS! Response: {content}")
                return True
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_azure_connection())
    
    if not success:
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING TIPS:")
        print("=" * 70)
        print("1. Verify your API key is correct and not expired")
        print("2. Check that the endpoint URL is correct (no trailing slash)")
        print("3. Ensure the deployment name matches your Azure OpenAI deployment")
        print("4. Confirm the API version is supported")
        print("5. Check if your Azure subscription is active")
        print("6. Verify network connectivity to Azure")
        print("=" * 70)
