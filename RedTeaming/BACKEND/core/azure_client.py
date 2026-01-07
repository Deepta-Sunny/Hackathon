"""
Azure OpenAI client for generating attack prompts and analyzing responses.
"""

import json
import httpx
from typing import Optional

from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


class AzureOpenAIClient:
    """
    Client for Azure OpenAI API calls with robust error handling.
    
    Features:
    - Automatic prompt truncation to avoid token limits
    - Error tracking and fallback responses
    - Temperature and token configuration
    """
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.api_key = AZURE_OPENAI_API_KEY
        self.deployment = AZURE_OPENAI_DEPLOYMENT
        self.api_version = AZURE_OPENAI_API_VERSION
        self.client: Optional[httpx.AsyncClient] = None
        
        # Statistics
        self.error_count = 0
        self.success_count = 0
        
        # Global token counters
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=120.0)
        return self.client
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate response from Azure OpenAI.
        
        Args:
            system_prompt: System role instructions
            user_prompt: User message
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            str: Generated response or fallback JSON on error
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        # No truncation - send full prompts to ensure classification rules aren't cut off
        print(f"    [INFO] System prompt: {len(system_prompt)} chars, User prompt: {len(user_prompt)} chars")
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            client = await self._get_client()
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            self.success_count += 1
            
            # Track token usage
            usage = result.get('usage', {})
            if usage:
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)
                
                # Update global counters
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                
                # Print real-time token usage
                print(f"    💰 Tokens: +{input_tokens} input, +{output_tokens} output, +{total_tokens} total | "
                      f"Running Totals: {self.total_input_tokens:,} input, {self.total_output_tokens:,} output, "
                      f"{self.total_input_tokens + self.total_output_tokens:,} total")
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            self.error_count += 1
            
            # Get detailed error message from Azure
            error_detail = ""
            status_code = "unknown"
            is_content_filter = False
            try:
                if hasattr(e, 'response'):
                    status_code = e.response.status_code
                    error_body = e.response.text
                    
                    # Check if this is a content filter violation
                    if '"code":"content_filter"' in error_body or '"ResponsibleAIPolicyViolation"' in error_body:
                        is_content_filter = True
                    
                    error_detail = f"\nAzure Response ({status_code}): {error_body[:500]}"
            except:
                pass
            
            print(f"⚠️ Azure API Error #{self.error_count}: {str(e)}{error_detail}")
            
            # For content filter violations, return a special marker instead of JSON
            if is_content_filter:
                return "[CONTENT_FILTER_VIOLATION] Azure OpenAI blocked this prompt due to content safety policies. This indicates the prompt contains potentially harmful content that was filtered."
            
            # Return a safe fallback JSON response for other errors
            fallback = {
                "risk_category": 2,
                "risk_explanation": f"Azure API error ({status_code}) - using safe default",
                "vulnerability_type": "api_error",
                "response_source": "error_fallback",
                "information_leaked": [],
                "context_exploitation": "no",
                "adaptation_needed": False,
                "learned_from_response": [f"Azure API unavailable: {str(e)[:100]}"]
            }
            return json.dumps(fallback)
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            
        if self.success_count > 0 or self.error_count > 0:
            print(f"\n📊 Azure API Stats: {self.success_count} success, {self.error_count} errors")
            print(f"💰 Total Token Usage:")
            print(f"   Input tokens:  {self.total_input_tokens:,}")
            print(f"   Output tokens: {self.total_output_tokens:,}")
            print(f"   Total tokens:  {self.total_input_tokens + self.total_output_tokens:,}")
            
            # Cost estimate (Azure OpenAI GPT-4 pricing)
            input_cost = (self.total_input_tokens / 1000) * 0.03  # $0.03 per 1K
            output_cost = (self.total_output_tokens / 1000) * 0.06
            total_cost = input_cost + output_cost
            print(f"   Estimated cost: ${total_cost:.4f}")
    
    def get_stats(self):
        """Get API call statistics."""
        return {
            "success": self.success_count,
            "errors": self.error_count,
            "total": self.success_count + self.error_count,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }
