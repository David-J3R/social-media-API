import pytest
from fastapi import BackgroundTasks, status
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


# Test user registration returns confirmation URL
@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    # spy allow us to look at a function call without changing its behavior
    spy = mocker.spy(BackgroundTasks, "add_task")

    await register_user(async_client, "test@example.com", "NotSecure123!")

    confirmation_url = str(spy.call_args[1]["confirmation_url"])
    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_200_OK
    assert "Email confirmed successfully" in response.json()["detail"]


# Test User return invalid confirmation token
@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/confirm/InvalidToken123")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test user return an expired confirmation token
@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("socialapi.security.confirm_token_expiry_minutes", return_value=-1)
    spy = mocker.spy(BackgroundTasks, "add_task")

    await register_user(async_client, "test@example.com", "NotSecure123!")

    confirmation_url = str(spy.call_args[1]["confirmation_url"])
    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        # using data since OAuth2PasswordRequestForm expects form data
        "/token",
        data={"username": "example@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test User login with confirmation
@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        "/token",
        # using data since OAuth2PasswordRequestForm expects form data
        data={
            "username": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK


# Test User login with unconfirmed email
@pytest.mark.anyio
async def test_login_user_unconfirmed(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        # using data since OAuth2PasswordRequestForm expects form data
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
