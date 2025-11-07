import logging

from fastapi import APIRouter, HTTPException, status

from socialapi.database import database, user_table
from socialapi.models.user import UserIn
from socialapi.security import (
    authenticate_user,
    create_access_token,
    get_hash_password,
    get_user,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Essential to hash the password before storing it
    hashed_password = get_hash_password(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    # Log the registration attempt
    logger.debug(query)

    await database.execute(query)
    return {"detail": "User registered successfully."}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)  # type: ignore
    access_token = create_access_token(email=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
