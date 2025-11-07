from pydantic import BaseModel


# we are going to do it the other way around from the post model
# because we don't want to expose password hashes
class User(BaseModel):
    id: int | None = None
    email: str


# input model for creating a user
class UserIn(User):
    password: str
