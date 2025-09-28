from fastapi import FastAPI

from socialapi.models.post import UserPost, UserPostIn

app = FastAPI()

# Temporary in-memory storage
posts_table = {}


@app.post("/post", response_model=UserPost)
async def create_post(post: UserPostIn):
    data = post.model_dump()  # Use "post.dict()" for Pydantic v1
    last_record_id = len(posts_table)
    new_post = {**data, "id": last_record_id}
    posts_table[last_record_id] = new_post  # Store the new post
    return new_post


@app.get("/post", response_model=list[UserPost])  # List of posts
async def get_all_posts():
    return list(posts_table.values())
