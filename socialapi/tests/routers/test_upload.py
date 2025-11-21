import contextlib
import pathlib

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.fixture()
def sample_image(fs) -> pathlib.Path:
    """Create a sample image file in the fake filesystem."""
    # Create the assets directory if it doesn't exist
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()

    # fs is the pyfakefs filesystem fixture. Create the file in the fake filesystem
    fs.create_file(path)

    return path


# Fixture to fake b2 upload_file function
@pytest.fixture(autouse=True)
def mock_b2_upload_file(mocker):
    return mocker.patch(
        "socialapi.routers.upload.b2_upload_file", return_value="https://b2.fake.com"
    )


@pytest.fixture(autouse=True)
async def aiofiles_mock_open(mocker, fs):
    """Mock aiofiles.open to work with pyfakefs."""

    mock_open = mocker.patch("aiofiles.open")

    # Define an async context manager to mimic aiofiles behavior
    @contextlib.asynccontextmanager
    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.AsyncMock(name=f"async_file_open:{fname!r}/{mode!r}")

        # Use pyfakefs to open the file and set read/write side effects
        with open(fname, mode) as fin:
            out_fs_mock.read.side_effect = fin.read
            out_fs_mock.write.side_effect = fin.write
            yield out_fs_mock

    mock_open.side_effect = async_file_open
    return mock_open


# Helper function to call the upload endpoint
async def call_upload_endpoint(
    async_client: AsyncClient, token: str, sample_image: pathlib.Path
):
    """Helper function to call the upload endpoint."""
    return await async_client.post(
        "/upload",
        files={"file": open(sample_image, "rb")},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.anyio
async def test_upload_image(
    async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path
):
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["file_url"] == "https://b2.fake.com"
