import datetime
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from socialapi.database import database, user_table

logger = logging.getLogger(__name__)

# Grab token from the Authorization header
# This is used in routes to get the token
# if we do oauth2_scheme() we get the token string
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Access Token (JWT) Management ---
# Not a good practice to hardcode secret keys in code.
# In production, use environment variables or secure vaults.
SECRET_KEY = "9b73b6f3c4d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8091a2b3c4d5e6f7"
ALGORITHM = "HS256"


def access_token_expiry_minutes() -> int:
    return 30


def create_access_token(email: str) -> str:
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=access_token_expiry_minutes()
    )
    # Create JWT token
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Password Hashing Context ---
pwd_context = CryptContext(schemes=["bcrypt"])


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # the plain_password must be verified using the same hashing algorithm as used in hash_password
    return pwd_context.verify(plain_password, hashed_password)


# --- User Retrieval ---
async def get_user(email: str):
    # Log the attempt to retrieve a user
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


# --- Authentication Functionality ---
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user.password):
        raise credentials_exception
    return user


# get current user from token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e

    user = await get_user(email)
    if user is None:
        raise credentials_exception
    return user
