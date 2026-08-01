from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, status
from typing import List

from blogs_api.schemas import PostCreate, PostResponse

app = FastAPI(title="Blogs API")


# Temporary in-memory storage for blog posts
fake_posts_db: List[PostResponse] = []


@app.get("/")
def read_root():
    """A simple greeting endpoint."""
    return {"message": "Welcome to the Blogs API"}

@app.post("/posts/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    """Create a new blog post."""
    # In a real application, you would save this to a database
    new_id = len(fake_posts_db) + 1
    current_time = datetime.now()

    # Conver Pydantic data into a standard dictionary
    new_post = {
        "id": new_id,
        **post.model_dump(),
        "created_at": current_time,
        "updated_at": current_time,
    }
    
    fake_posts_db.append(new_post)
    return new_post

@app.get("/posts/", response_model=List[PostResponse])
def get_posts():
    """Retrieve all blog posts."""
    return fake_posts_db

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, q: str = None):
    """Retrieve a specific blog post by its ID."""
    # In a real application, you would fetch this from a database
    for post in fake_posts_db:
        if post["id"] == post_id:
            return post
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")

def main():
    uvicorn.run("blogs_api.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
