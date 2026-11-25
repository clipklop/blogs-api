from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from blogs_api.models import Post


def published_posts():
    return Post.state == "published"


def readable_posts(user_id: int | None):
    if user_id is None:
        return published_posts()
    return or_(published_posts(), Post.owner_id == user_id)


def lock_post(db: Session, post_id: int, *, published_only: bool = False):
    statement = select(Post).where(Post.id == post_id)
    if published_only:
        statement = statement.where(published_posts())
    return db.scalar(statement.with_for_update().execution_options(populate_existing=True))
