import pytest
from httpx import AsyncClient


# Helper function to create a post
async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/post", json={"body": body})
    return response.json()


# Fixture to create a post before each test
@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test Post", async_client)


# Test create_post endpoint
@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "My first Test Post"

    response = await async_client.post("/post", json={"body": body})

    assert response.status_code == 201
    # using <= to check if the expected items are in the response
    assert {"id": 0, "body": body}.items() <= response.json().items()


# Test missing body in create_post
@pytest.mark.anyio
async def test_create_post_missing_body(async_client: AsyncClient):
    response = await async_client.post("/post", json={})

    assert response.status_code == 422  # Unprocessable Entity


# Test get_all_posts endpoint
@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")

    assert response.status_code == 200
    assert response.json() == [created_post]


# ----- Test Comments ----- #


# Helper function to create a comment
async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/comment", json={"body": body, "post_id": post_id}
    )
    return response.json()


# Fixture to create a comment before each test
@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    return await create_comment("Test Comment", created_post["id"], async_client)


# Test create_comment endpoint
@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "My first Test Comment"

    response = await async_client.post(
        "/comment", json={"body": body, "post_id": created_post["id"]}
    )

    assert response.status_code == 201
    assert {
        "id": 0,
        "body": body,
        "post_id": created_post["id"],
    }.items() <= response.json().items()


# Test missing body in create_comment
@pytest.mark.anyio
async def test_create_comment_missing_body(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.post("/comment", json={"post_id": created_post["id"]})

    assert response.status_code == 422  # Unprocessable Entity


# Test get all comments for a post
@pytest.mark.anyio
async def test_get_comments_for_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comments")

    assert response.status_code == 200
    # Check if the created comment is in the response
    assert response.json() == [created_comment]


# Test get comments for a post with no comments
@pytest.mark.anyio
async def test_get_comments_for_post_empty(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comments")

    assert response.status_code == 200  # OK
    assert response.json() == []  # No comments yet


# Test get comments for a non-existent post
@pytest.mark.anyio
async def test_get_comments_for_nonexistent_post(async_client: AsyncClient):
    response = await async_client.get("/post/999/comments")

    assert response.status_code == 404  # Not Found


# Test get_post_with_comments endpoint
@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert response.json() == {"post": created_post, "comments": [created_comment]}


# Test get_post_with_comments for non-existent post
@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/1")
    assert response.status_code == 404  # Not Found
