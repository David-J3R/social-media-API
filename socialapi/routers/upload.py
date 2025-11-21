import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status

from socialapi.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()


# FLOW: client -> server (tempfile) -> B2 -> delete tempfile


CHUNK_SIZE = 1024 * 1024  # 1MB


# Endpoint to handle file uploads
# The file type UploadFile is a pipe that allows streaming large files
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile):
    """Endpoint to upload a file to Backblaze B2."""
    try:
        # tempfile.NamedTemporaryFile is used to create a temporary file, itself is an empty container
        with tempfile.NamedTemporaryFile() as temp_file:
            # Get the name of the temporary file
            filename = temp_file.name
            logger.debug(f"Saving uploaded file temporarily to {filename}")

            # Write (write binary) in the temporary file and read from the UploadFile stream
            async with aiofiles.open(filename, "wb") as f:  # "wb" means write binary
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            # After writing the file to a temporary location, upload it to B2
            file_url = b2_upload_file(local_file=filename, file_name=file.filename)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file.",
        )

    return {"detail": f"Successfully uploaded {file.filename}", "file_url": file_url}
