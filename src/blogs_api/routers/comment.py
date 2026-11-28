from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from blogs_api.database import get_db
from blogs_api.models import Comment, Post, User
from blogs_api.oauth2 import get_current_user, optional_oauth2_scheme, resolve_post_reader
from blogs_api.post_access import lock_post, readable_posts
from blogs_api.schemas import CommentBody, CommentResponse


class CommentRoute(APIRoute):
    def get_route_handler(self):
        handle = super().get_route_handler()

        async def handle_comment(request: Request) -> Response:
            try:
                return await handle(request)
            except RequestValidationError as exc:
                try:
                    return await request_validation_exception_handler(request, exc)
                except ValueError:
                    # Malformed JSON strings or numbers cannot be echoed in a JSON response.
                    return JSONResponse(
                        status_code=422,
                        content={"detail": [{"loc": ["body"], "msg": "Invalid comment request", "type": "value_error"}]},
                    )

        return handle_comment


router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Comments"], route_class=CommentRoute)

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalBearer = Annotated[str | None, Depends(optional_oauth2_scheme)]
ResourceID = Annotated[int, Path(ge=1, le=2_147_483_647)]


@router.get("", response_model=list[CommentResponse], openapi_extra={"security": [{}]})
def list_comments(
    post_id: ResourceID,
    db: DbSession,
    request: Request,
    token: OptionalBearer,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=2_147_483_647)] = 0,
):
    reader = resolve_post_reader(request, db, token)
    page = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc(), Comment.id.desc())
        .offset(offset)
        .limit(limit)
        .subquery()
    )
    page_comment = aliased(Comment, page)
    statement = (
        select(page_comment)
        .select_from(Post)
        .outerjoin(page_comment, page_comment.post_id == Post.id)
        .where(Post.id == post_id, readable_posts(reader.id if reader else None))
        .order_by(page_comment.created_at.desc(), page_comment.id.desc())
    )
    comments = db.scalars(statement).all()
    if not comments:
        raise HTTPException(404, "Post not found")
    return [comment for comment in comments if comment is not None]


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: ResourceID, payload: CommentBody, db: DbSession, user: CurrentUser):
    if lock_post(db, post_id, published_only=True) is None:
        raise HTTPException(404, "Post not found")
    comment = Comment(post_id=post_id, author_id=user.id, body=payload.body)
    db.add(comment)
    db.flush()
    result = CommentResponse.model_validate(comment)
    db.commit()
    return result


def comment_for_mutation(
    db: Session, post_id: int, comment_id: int, user_id: int, *, allow_post_author: bool = False
) -> Comment:
    post = lock_post(db, post_id)
    if post is None or (post.state != "published" and post.owner_id != user_id):
        raise HTTPException(404, "Post not found")
    comment = db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))
    if comment is None:
        raise HTTPException(404, "Comment not found")
    if comment.author_id != user_id and not (allow_post_author and post.owner_id == user_id):
        raise HTTPException(403, "Not authorized to modify this comment")
    return comment


@router.patch("/{comment_id}", response_model=CommentResponse)
def edit_comment(
    post_id: ResourceID, comment_id: ResourceID, payload: CommentBody, db: DbSession, user: CurrentUser
):
    comment = comment_for_mutation(db, post_id, comment_id, user.id)
    comment.body = payload.body
    comment.updated_at = datetime.now(timezone.utc)
    result = CommentResponse.model_validate(comment)
    db.commit()
    return result


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_comment(post_id: ResourceID, comment_id: ResourceID, db: DbSession, user: CurrentUser):
    db.delete(comment_for_mutation(db, post_id, comment_id, user.id, allow_post_author=True))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
