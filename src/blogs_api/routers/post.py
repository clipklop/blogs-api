from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.oauth2 import get_current_user
from blogs_api.schemas import PostCreate, PostResponse, PostUpdate, PostWithVotes
from blogs_api.slugs import make_slug

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]
router = APIRouter(prefix="/posts", tags=["Posts"])


def posts_with_votes(db: Session):
    vote_counts = db.query(
        models.Vote.post_id.label("post_id"),
        func.count().label("votes"),
    ).group_by(models.Vote.post_id).subquery()
    return db.query(models.Post, func.coalesce(vote_counts.c.votes, 0)).outerjoin(
        vote_counts, vote_counts.c.post_id == models.Post.id
    )


def post_response(row) -> PostWithVotes:
    post, votes = row
    return PostWithVotes(**PostResponse.model_validate(post).model_dump(), votes=votes)


def owned_post(post_id: int, db: Session, user: models.User) -> models.Post:
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail=f"Post with ID {post_id} not found")
    if post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this post")
    return post


@router.get("/", response_model=list[PostWithVotes])
def get_posts(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    published: bool | None = None,
    search: Annotated[str | None, Query(min_length=1, max_length=1000)] = None,
    sort: Literal["newest", "oldest"] = "newest",
):
    query = posts_with_votes(db)
    if published is not None:
        query = query.filter(models.Post.published == published)
    if search is not None:
        query = query.filter(or_(
            models.Post.title.icontains(search, autoescape=True),
            models.Post.content.icontains(search, autoescape=True),
        ))
    order = (models.Post.created_at.asc(), models.Post.id.asc()) if sort == "oldest" else (
        models.Post.created_at.desc(), models.Post.id.desc()
    )
    return [post_response(row) for row in query.order_by(*order).offset(offset).limit(limit).all()]


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: DbSession, current_user: CurrentUser):
    db_post = models.Post(owner_id=current_user.id, slug=make_slug(post.title), **post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/slug/{slug}", response_model=PostWithVotes)
def read_post_by_slug(slug: str, db: DbSession):
    row = posts_with_votes(db).filter(models.Post.slug == slug).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_response(row)


@router.get("/{post_id}", response_model=PostWithVotes)
def read_post(post_id: int, db: DbSession, current_user: CurrentUser):
    row = posts_with_votes(db).filter(models.Post.id == post_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Post with ID {post_id} not found")
    return post_response(row)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostUpdate, db: DbSession, current_user: CurrentUser):
    db_post = owned_post(post_id, db, current_user)
    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_post(post_id: int, db: DbSession, current_user: CurrentUser):
    db.delete(owned_post(post_id, db, current_user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
