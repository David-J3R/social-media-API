from httpx import AsyncClient


# Helper function to create a post
async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/post",
        json={"body": body},
        # Add Authorization header with Bearer token for authentication
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


# Helper function to create a comment
async def create_comment(
    body: str, post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id},
        # Add Authorization header with Bearer token for authentication
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


# Helper function to like a post
async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/like",
        json={"post_id": post_id},
        # Add Authorization header with Bearer token for authentication
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()
