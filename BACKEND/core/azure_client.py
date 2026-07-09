"""Azure OpenAI client for generating attack prompts and analyzing responses."""

import httpx
import os
from typing import Optional

from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION
)


class AzureOpenAIClient:
    """
    Client for Azure OpenAI API calls with robust error handling.
    
    Features:
    - Direct, env-driven Azure OpenAI requests
    - Error tracking and token usage reporting
    - Optional reasoning and temperature fields
    """
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.api_key = AZURE_OPENAI_API_KEY
        self.deployment = AZURE_OPENAI_DEPLOYMENT_NAME
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

    def _build_url(self) -> str:
        """Build Azure OpenAI chat completions URL."""
        return f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        reasoning_effort: str = "medium",
        reasoning_summary: str = "concise"
    ) -> str:
        """Generate response from Azure OpenAI."""
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
            "max_completion_tokens": max_tokens
        }

        # Keep temperature optional via env flag for deployments that support custom values.
        include_temperature = os.getenv("AZURE_OPENAI_INCLUDE_TEMPERATURE", "false").lower() == "true"
        if include_temperature:
            payload["temperature"] = temperature

        # Optional reasoning controls for compatible deployments.
        # Ref shape:
        # additional_chat_options = {
        #   "reasoning": {"effort": "medium", "summary": "concise"}
        # }
        reasoning_enabled = os.getenv("AZURE_OPENAI_ENABLE_REASONING", "false").lower() == "true"
        if reasoning_enabled and reasoning_effort:
            payload["reasoning"] = {
                "effort": reasoning_effort,
                "summary": reasoning_summary
            }
        
        try:
            client = await self._get_client()
            url = self._build_url()
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            self.success_count += 1

            usage = result.get('usage', {})
            if usage:
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)

                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens

                print(f"    💰 Tokens: +{input_tokens} input, +{output_tokens} output, +{total_tokens} total | "
                      f"Running Totals: {self.total_input_tokens:,} input, {self.total_output_tokens:,} output, "
                      f"{self.total_input_tokens + self.total_output_tokens:,} total")

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            self.error_count += 1
            detail = ""
            if hasattr(e, "response") and getattr(e, "response", None) is not None:
                try:
                    detail = f"\nAzure Response ({e.response.status_code}): {(e.response.text or '')[:500]}"
                except Exception:
                    detail = ""
            print(f"⚠️ Azure API Error #{self.error_count}: {str(e)}{detail}")
            raise
    
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
