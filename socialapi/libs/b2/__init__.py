import logging
from functools import lru_cache

import b2sdk.v2 as b2

from socialapi.config import config

logger = logging.getLogger(__name__)


# Initialize B2 API with caching
@lru_cache()
def get_b2_api():
    """Initialize and return a Backblaze B2 API client."""
    logger.debug("Initializing Backblaze B2 API client.")
    info = b2.InMemoryAccountInfo()
    b2_api = b2.B2Api(info)

    b2_api.authorize_account("production", config.B2_KEY_ID, config.B2_APPLICATION_KEY)
    return b2_api


# Get bucket with caching
@lru_cache()
def get_b2_bucket(api: b2.B2Api):
    """Retrieve and return the Backblaze B2 bucket."""
    return api.get_bucket_by_name(config.B2_BUCKET_NAME)


# Upload file to B2
def b2_upload_file(local_file: str, file_name: str):
    """Upload a file to Backblaze B2"""
    api = get_b2_api()
    logger.debug(f"Uploading file {local_file} to Backblaze B2 as {file_name}.")

    # Get the bucket and upload the file
    uploaded_file = get_b2_bucket(api).upload_local_file(
        local_file=local_file,
        file_name=file_name,
    )

    # Get the download URL for the uploaded file
    download_url = api.get_download_url_for_fileid(uploaded_file.id_)
    logger.debug(
        f"Uploaded file {local_file} to B2 successfully. Download URL: {download_url}"
    )
    return download_url
