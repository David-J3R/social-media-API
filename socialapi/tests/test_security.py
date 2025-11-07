import pytest
from jose import jwt

from socialapi import security


# Using a async db fixture from conftest.py
# test_password_hashes is a synchronous test but
# it's automatically getting the async db fixture applied to it.
def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_hash_password(password))


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com")
    assert user is None


# --- Authentication Tests ---
def test_access_token_expiry_minutes():
    assert security.access_token_expiry_minutes() == 30


# test creating access token
def test_create_access_token():
    token = security.create_access_token("test@example.com")
    assert {"sub": "test@example.com"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


# test authenticating user
@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


# test authenticating user not found
@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.com", "password")


# test authenticating user with wrong password
@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrongpassword")


# test get current user from token
@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


# test get current user with invalid token
@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalidtoken")
