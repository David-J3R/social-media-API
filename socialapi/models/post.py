from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):  # Class inheritance
    id: int


# ----- Comments -----
class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
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
