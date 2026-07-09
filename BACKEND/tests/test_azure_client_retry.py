import json
import sys
import unittest
from unittest.mock import AsyncMock
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from azure_client import AzureOpenAIClient


def _http_status_error(status_code: int, body: str) -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://example.openai.azure.com/chat/completions")
    response = httpx.Response(status_code, request=request, text=body)
    return httpx.HTTPStatusError(
        f"Server error '{status_code}'",
        request=request,
        response=response
    )


def _success_response(content: str) -> httpx.Response:
    request = httpx.Request("POST", "https://example.openai.azure.com/chat/completions")
    payload = {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }
    return httpx.Response(
        200,
        request=request,
        headers={"Content-Type": "application/json"},
        content=json.dumps(payload).encode("utf-8")
    )


class AzureClientRetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_retries_transient_503_and_recovers(self):
        client = AzureOpenAIClient()
        client.retry_delay_seconds = 0

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=[
                _http_status_error(503, "upstream connect timeout"),
                _success_response("Recovered response")
            ]
        )
        client.client = mock_http_client

        result = await client.generate("system", "user", temperature=0.0, max_tokens=32)

        self.assertEqual(result, "Recovered response")
        self.assertEqual(mock_http_client.post.await_count, 2)
        self.assertEqual(client.success_count, 1)

    async def test_returns_fallback_after_retry_budget_exhausted(self):
        client = AzureOpenAIClient()
        client.retry_delay_seconds = 0

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=[
                _http_status_error(503, "temporary outage"),
                _http_status_error(503, "temporary outage"),
                _http_status_error(503, "temporary outage")
            ]
        )
        client.client = mock_http_client

        result = await client.generate("system", "user")
        parsed = json.loads(result)

        self.assertEqual(mock_http_client.post.await_count, 3)
        self.assertEqual(parsed["response_source"], "error_fallback")
        self.assertIn("503", parsed["risk_explanation"])

    async def test_content_filter_error_does_not_retry(self):
        client = AzureOpenAIClient()
        client.retry_delay_seconds = 0

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=[
                _http_status_error(
                    400,
                    '{"error":{"code":"content_filter","message":"Blocked by policy"}}'
                )
            ]
        )
        client.client = mock_http_client

        result = await client.generate("system", "user")

        self.assertTrue(result.startswith("[CONTENT_FILTER_VIOLATION]"))
        self.assertEqual(mock_http_client.post.await_count, 1)


if __name__ == "__main__":
    unittest.main()
