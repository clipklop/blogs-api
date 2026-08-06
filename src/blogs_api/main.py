from typing import Annotated, List
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.schemas import PostCreate, PostResponse, PostUpdate
from blogs_api.database import Base, get_db, engine

app = FastAPI(title="Blogs API")


# Temporary in-memory storage for blog posts
# fake_posts_db: List[PostResponse] = []

# Temporary for initial prototyping
Base.metadata.create_all(bind=engine)
DbSession = Annotated[Session, Depends(get_db)]

def find_index(post_id: int):
    for i, p in enumerate(fake_posts_db):
        if p['id'] == post_id:
            return i
    return None

@app.get("/db-health")
def read_db_health(db: Session = Depends(get_db)):
    """Check the health of the database."""
    try:
        # Perform a simple query to check database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

@app.get("/posts/", response_model=List[PostResponse])
def get_posts(db: DbSession):
    """Retrieve all blog posts."""
    # return fake_posts_db
    return db.query(models.Post).all()

@app.post("/posts/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: DbSession):
    """Create a new blog post."""
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# def create_post(post: PostCreate):
#     """Create a new blog post."""
#     # In a real application, you would save this to a database
#     new_id = len(fake_posts_db) + 1
#     current_time = datetime.now()

#     # Conver Pydantic data into a standard dictionary
#     new_post = {
#         "id": new_id,
#         **post.model_dump(),
#         "created_at": current_time,
#         "updated_at": current_time,
#     }
    
#     fake_posts_db.append(new_post)
#     return new_post

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, q: str = None):
    """Retrieve a specific blog post by its ID."""
    # In a real application, you would fetch this from a database
    for post in fake_posts_db:
        if post["id"] == post_id:
            return post
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")

@app.patch("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostUpdate):
    """Partially update a specific blog post by its ID."""
    index = find_index(post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    post_data = fake_posts_db[index]
    update_data = post.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        post_data[key] = value
    post_data["updated_at"] = datetime.now()
    return post_data

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    """Delete a specific blog post by its ID."""
    index = find_index(post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    fake_posts_db.pop(index)
    return {"message": f"Post with ID {post_id} deleted successfully"}


def main():
    uvicorn.run("blogs_api.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
