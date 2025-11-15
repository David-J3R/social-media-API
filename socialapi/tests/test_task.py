import httpx
import pytest
from fastapi import status

from socialapi.task import APIResponseError, send_simple_email


@pytest.mark.asyncio
async def test_send_simple_email(mock_httpx_client):
    await send_simple_email("test@example.com", "Test Subject", "Test Body")

    # Assert that the HTTP POST request was made once
    mock_httpx_client.post.assert_called()


# Test api server error handling
@pytest.mark.asyncio
async def test_send_simple_email_api_error(mock_httpx_client):
    # overwrite the mock to simulate an API error
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="",
        request=httpx.Request("POST", "//"),
    )

    # Expect an APIResponseError to be raised
    with pytest.raises(APIResponseError):
        await send_simple_email("test@example.com", "Test Subject", "Test Body")
