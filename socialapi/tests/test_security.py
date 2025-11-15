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


def test_confirm_token_expiry_minutes():
    assert security.confirm_token_expiry_minutes() == 1440


# test creating access token
def test_create_access_token():
    token = security.create_access_token("test@example.com")
    assert {"sub": "test@example.com", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_create_confirmation_token():
    token = security.create_confirmation_token("test@example.com")
    assert {"sub": "test@example.com", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


# Test get subject for token type - valid token confirmation
def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


# Test get subject for token type - valid token access
def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


# Test get subject for token type - expire token type
def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("socialapi.security.access_token_expiry_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token has expired" == exc_info.value.detail


# Test get subject for token type - invalid token
def test_get_subject_for_token_type_invalid():
    token = "invalidtoken"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is invalid" == exc_info.value.detail


# Test missing sub in token
def test_get_subject_for_token_type_missing_sub():
    email = "test@example.com"
    token = security.create_access_token(email)
    # Decode token to manipulate payload
    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]
    # Re-encode token without 'sub'
    manipulated_token = jwt.encode(
        payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM
    )

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(manipulated_token, "access")
    assert "Token is missing 'sub' field" == exc_info.value.detail


# Test wrong type of token
def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token has incorrect type, expected: 'access'" == exc_info.value.detail


# test authenticating user
@pytest.mark.anyio
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(
        confirmed_user["email"], confirmed_user["password"]
    )
    assert user.email == confirmed_user["email"]


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


# test get the current user with invalid token type
@pytest.mark.anyio
async def test_get_current_user_invalid_token_type(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])
    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
