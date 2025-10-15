from fastapi import APIRouter, HTTPException

from socialapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()

# Temporary in-memory storage
posts_table = {}
comments_table = {}


def find_post(post_id: int):
    return posts_table.get(post_id)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()  # Use "post.dict()" for Pydantic v1
    last_record_id = len(posts_table)
    new_post = {**data, "id": last_record_id}
    posts_table[last_record_id] = new_post  # Store the new post
    return new_post


@router.get("/post", response_model=list[UserPost])  # List of posts
async def get_all_posts():
    return list(posts_table.values())


# ---- Comments -----
@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    # Validate that the post exists
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    last_record_id = len(comments_table)
    new_comment = {**data, "id": last_record_id}
    comments_table[last_record_id] = new_comment
    return new_comment


@router.get("/post/{post_id}/comments", response_model=list[Comment])
# pydantic detects the post_id from the path
async def get_comments_on_post(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [
        comment for comment in comments_table.values() if comment["post_id"] == post_id
    ]


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # The output must match the UserPostWithComments model
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
