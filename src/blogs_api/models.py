from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, Integer, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from blogs_api.database import Base


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_name", ForeignKey("tags.name", ondelete="CASCADE"), primary_key=True),
    Index("ix_post_tags_tag_name", "tag_name"),
)


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("state IN ('draft', 'published', 'archived')", name="ck_posts_state"),
        CheckConstraint("state <> 'published' OR published_at IS NOT NULL", name="ck_posts_publication_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(9), server_default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rating: Mapped[float] = mapped_column(default=0.0)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner: Mapped[User] = relationship("User", back_populates="posts")
    tag_records: Mapped[list[Tag]] = relationship(secondary=post_tags, viewonly=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
    )

    @property
    def tags(self) -> list[str]:
        return sorted(tag.name for tag in self.tag_records)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="owner", passive_deletes=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
