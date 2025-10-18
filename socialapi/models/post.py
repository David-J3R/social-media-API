from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):  # Class inheritance
    # Remember to set model_config for Pydantic v2
    # and for ORM mode
    model_config = ConfigDict(
        from_attributes=True
    )  # for Pydantic dealing with ORM objects
    id: int


# ----- Comments -----
class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    model_config = ConfigDict(
        from_attributes=True
    )  # for Pydantic dealing with ORM objects
    id: int


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]


# Example of object
"""
{
"post": {"id": 1, "body": "My first post"},
"comments": [{"id": 1, "post_id": 1, "body": "Great post!"}, {"id": 2, "post_id": 2, "body": "Thanks for sharing!"}]
}
"""
