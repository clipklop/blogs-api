from typing import Annotated, List

from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, HTTPException, status, Depends, APIRouter, Query

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.oauth2 import get_current_user
from blogs_api.schemas import (
    PostCreate, PostResponse, PostUpdate
)

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[PostResponse])
def get_posts(
    db: DbSession,
    limit: Annotated[int, Query(gt=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Retrieve all blog posts."""
    return (
        db.query(models.Post)
        .order_by(
            models.Post.created_at.desc(),
            models.Post.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate, 
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new blog post."""
    print(current_user)
    db_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/{post_id}", response_model=PostResponse)
def read_post(
    post_id: int, 
    db: DbSession,
):
    """Retrieve a specific blog post by its ID."""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    return post

@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int, 
    post: PostUpdate, 
    db: DbSession,
    current_user: CurrentUser
):
    """Partially update a specific blog post by its ID."""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")
    # Ensure that only the fields provided in the request are updated
    update_data = post.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # Update only the fields that are provided in the request
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, 
    db: DbSession,
    current_user: CurrentUser
):
    """Delete a specific blog post by its ID."""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": f"Post with ID {post_id} deleted successfully"}
