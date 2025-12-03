import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from socialapi import task
from socialapi.database import database, user_table
from socialapi.models.user import UserIn
from socialapi.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_hash_password,
    get_subject_for_token_type,
    get_user,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
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
    # Send Confirmation Email
    background_tasks.add_task(
        task.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),  # type: ignore
    )
    return {"detail": "User created. Please confirm your email."}


@router.post("/token")
# form_data will have username and password attributes
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)  # type: ignore
    access_token = create_access_token(email=user.email)  # type: ignore
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    """ "Endpoint to confirm user's email address using a token"""
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )

    # Log the email confirmation attempt
    logger.debug(query)

    await database.execute(query)
    return {"detail": "Email confirmed successfully"}
