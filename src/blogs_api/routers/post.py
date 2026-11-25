from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.oauth2 import get_current_user, optional_oauth2_scheme, resolve_post_reader
from blogs_api.post_access import lock_post, published_posts, readable_posts
from blogs_api.schemas import PostCreate, PostPublication, PostResponse, PostState, PostUpdate, PostWithVotes
from blogs_api.slugs import make_slug

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]
OptionalBearer = Annotated[str | None, Depends(optional_oauth2_scheme)]
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
    post = lock_post(db, post_id)
    if post is None or (post.state != "published" and post.owner_id != user.id):
        raise HTTPException(status_code=404, detail=f"Post with ID {post_id} not found")
    if post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this post")
    return post


@router.get("/", response_model=list[PostWithVotes], openapi_extra={"security": [{}]})
def get_posts(
    db: DbSession,
    request: Request,
    token: OptionalBearer,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    scope: Annotated[Literal["public", "mine"], Query(description="Use a bearer token for mine")] = "public",
    state: PostState | None = None,
    search: Annotated[str | None, Query(min_length=1, max_length=1000)] = None,
    sort: Literal["newest", "oldest"] = "newest",
):
    query = posts_with_votes(db)
    if "published" in request.query_params:
        raise RequestValidationError([{
            "type": "extra_forbidden", "loc": ("query", "published"),
            "msg": "Use the state filter instead of published", "input": request.query_params["published"],
        }])
    if scope == "mine":
        user = resolve_post_reader(request, db, token, required=True)
        query = query.filter(models.Post.owner_id == user.id)
    else:
        if state not in (None, "published"):
            raise RequestValidationError([{
                "type": "value_error", "loc": ("query", "state"),
                "msg": "Private states require scope=mine", "input": state,
            }])
        query = query.filter(published_posts())
    if state is not None:
        query = query.filter(models.Post.state == state)
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


@router.get("/slug/{slug}", response_model=PostWithVotes, openapi_extra={"security": [{}]})
def read_post_by_slug(slug: str, db: DbSession, request: Request, token: OptionalBearer):
    user = resolve_post_reader(request, db, token)
    row = posts_with_votes(db).filter(models.Post.slug == slug, readable_posts(user.id if user else None)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_response(row)


@router.get("/{post_id}", response_model=PostWithVotes)
def read_post(post_id: int, db: DbSession, current_user: CurrentUser):
    row = posts_with_votes(db).filter(models.Post.id == post_id, readable_posts(current_user.id)).first()
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


@router.put("/{post_id}/publication", response_model=PostResponse)
def set_publication(post_id: int, publication: PostPublication, db: DbSession, current_user: CurrentUser):
    post = owned_post(post_id, db, current_user)
    if post.state == publication.state:
        return post
    if post.state == "archived" and publication.state == "published":
        raise HTTPException(status_code=409, detail="Restore archived posts to draft before publishing")
    post.state = publication.state
    now = datetime.now(timezone.utc)
    post.updated_at = now
    if post.state == "published" and post.published_at is None:
        post.published_at = now
    db.flush()
    db.refresh(post)
    result = PostResponse.model_validate(post)
    db.commit()
    return result


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_post(post_id: int, db: DbSession, current_user: CurrentUser):
    db.delete(owned_post(post_id, db, current_user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
