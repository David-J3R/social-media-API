import pytest
from fastapi import status
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


# Test registering a new user
@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "NotSecure123!")
    assert response.status_code == 201
    assert "User registered successfully." in response.json()["detail"]


# Test registering a user with an existing email
@pytest.mark.anyio
async def test_register_existing_user(async_client: AsyncClient, registered_user: dict):
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"]
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "A user with this email already exists." in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/token", json={"email": "test@example.com", "password": "NotSecure123!"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
