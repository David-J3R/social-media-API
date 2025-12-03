import httpx
import pytest
from databases import Database
from fastapi import status

from socialapi.database import post_table
from socialapi.task import (
    APIResponseError,
    _generate_cute_creature_api,
    generate_and_add_to_post,
    send_simple_email,
)


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


# ----- Test DeepAI integration ----- #


@pytest.mark.anyio
async def test_generate_cute_creature_api_success(mock_httpx_client):
    json_data = {"output_url": "http://example.com/image.jpg"}

    # Mock successful API response
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=status.HTTP_200_OK,
        json=json_data,
        request=httpx.Request("POST", "//"),
    )

    result = await _generate_cute_creature_api("A cat in a hat")

    assert result == json_data


# Test DeepAI API error
@pytest.mark.anyio
async def test_generate_cute_creature_api_server_error(mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="",
        request=httpx.Request("POST", "//"),
    )

    with pytest.raises(APIResponseError, match="DeepAI API returned an error: 500"):
        await _generate_cute_creature_api("A cat in a hat")


# Test DeepAI API invalid JSON response
@pytest.mark.anyio
async def test_generate_cute_creature_api_json_error(mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=status.HTTP_200_OK,
        content="Invalid JSON",
        request=httpx.Request("POST", "//"),
    )

    with pytest.raises(APIResponseError, match="Error parsing DeepAI API response"):
        await _generate_cute_creature_api("A cat in a hat")


# Test adding image to post
@pytest.mark.anyio
async def test_generate_and_add_to_post_success(
    mock_httpx_client, created_post: dict, confirmed_user: dict, db: Database
):
    json_data = {"output_url": "http://example.com/generated_image.jpg"}

    # Mock successful DeepAI API response
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=status.HTTP_200_OK,
        json=json_data,
        request=httpx.Request("POST", "//"),
    )

    await generate_and_add_to_post(
        email=confirmed_user["email"],
        post_id=created_post["id"],
        post_url="http://testserver/post/1",
        database=db,
        prompt="A cute dog",
    )

    # Verify that the post was updated with the image URL
    query = post_table.select().where(post_table.c.id == created_post["id"])

    updated_post = await db.fetch_one(query)

    assert updated_post.image_url == json_data["output_url"]


# Test generate_and_add_to_post with DeepAI API error
