from typing import Annotated, List
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.schemas import PostCreate, PostResponse, PostUpdate
from blogs_api.database import Base, get_db, engine, settings

app = FastAPI(title="Blogs API")

# Temporary for initial prototyping. In a production application, use Alembic for database migrations.
try:
    Base.metadata.create_all(bind=engine)
except OperationalError:
    raise RuntimeError(
        "Database startup failed: PostgreSQL could not be reached "
        f"(connection timeout: {settings.database_connect_timeout}s). "
        "Make sure PostgreSQL is running and DATABASE_URL is correct."
    ) from None

DbSession = Annotated[Session, Depends(get_db)]

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
    return db.query(models.Post).all()

@app.post("/posts/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: DbSession):
    """Create a new blog post."""
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: DbSession, q: str | None = None):
    """Retrieve a specific blog post by its ID."""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    return post

@app.patch("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostUpdate, db: DbSession):
    """Partially update a specific blog post by its ID."""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    # Ensure that only the fields provided in the request are updated
    update_data = post.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # Update only the fields that are provided in the request
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DbSession):
    """Delete a specific blog post by its ID."""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    db.delete(db_post)
    db.commit()
    return {"message": f"Post with ID {post_id} deleted successfully"}


def main():
    uvicorn.run("blogs_api.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
