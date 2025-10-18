import os
from typing import AsyncGenerator, Generator

import pytest

# TestClient simulates requests to the FastAPI app
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"
from socialapi.database import database
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
