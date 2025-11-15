import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest

# TestClient simulates requests to the FastAPI app
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Request, Response

os.environ["ENV_STATE"] = "test"
from socialapi.database import database, user_table
from socialapi.main import app  # noqa: E402


# Configure pytest to use asyncio for async tests
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# Create a TestClient instance for synchronous tests
@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


# Fixture to manage the in-memory database state
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    # Setup: Clear the in-memory tables before each test
    await database.connect()
    yield
    # Teardown: Clear the in-memory tables after each test
    await database.disconnect()


# Create an AsyncClient instance for asynchronous tests
@pytest.fixture()
# Dependency Injection:
async def async_client(client) -> AsyncGenerator:
    # `AsyncClient` is from the `httpx` library and is the async equivalent of `TestClient`.
    # `async with` creates a context where the client is set up and will be properly closed afterward.
    async with AsyncClient(
        # Use ASGITransport to allow for async testing
        base_url=client.base_url,
        transport=ASGITransport(app),
    ) as ac:
        yield ac
        # Once the test finishes, the `async with` block automatically handles the teardown/cleanup.


# --- User fixtures ---


# Register a user not confirmed
@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "NotSecure123!"}
    await async_client.post("/register", json=user_details)

    # Return with user id
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    assert user is not None, "User registration failed"
    user_details["id"] = user["id"]

    return user_details


# Register a user confirmed
@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


# grab a token using the api
@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    # pydantic use only the fields required for the model
    response = await async_client.post(
        "/token",
        # use the registered user's credentials to get a token
        data={
            "username": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    return response.json()["access_token"]


# Make sure to don't send real emails via mailgun during tests
@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    # Mock the AsyncClient used in socialapi.task to prevent real HTTP requests during tests
    mocked_client = mocker.patch("socialapi.task.httpx.AsyncClient")

    # Create a mock instance of AsyncClient
    mocked_async_client = Mock()
    # Configure the mock to return a successful response
    response = Response(status_code=200, content="", request=Request("POST", "//"))

    # Configure the mock to return a successful response
    # AsyncMock is used to mock async methods
    mocked_async_client.post = AsyncMock(return_value=response)

    # Because AsyncClient is used as an async context manager, we need to mock __aenter__ and __aexit__
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    # Return the mocked client for further assertions if needed
    return mocked_async_client
