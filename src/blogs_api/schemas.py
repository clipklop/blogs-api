import re
from typing import Annotated, Literal, Optional
from datetime import datetime, timezone

from pydantic import BeforeValidator, BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator


# Schema for incoming requests
PostState = Literal["draft", "published", "archived"]


def normalize_tag_name(value: str) -> str:
    name = value.strip()
    if len(name) > 32 or re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", name) is None:
        raise ValueError("Tag names must be 1 to 32 ASCII letters or digits with optional single hyphens")
    return name.lower()


def validate_tag_name(value: object) -> object:
    return normalize_tag_name(value) if isinstance(value, str) else value


TagName = Annotated[str, BeforeValidator(validate_tag_name), Field(strict=True)]


class PostTags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tags: list[TagName] = Field(max_length=10)


class CommentBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(strict=True, min_length=1, max_length=1000)

    @field_validator("body", mode="before")
    @classmethod
    def clean_body(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if "\0" in value or any(0xD800 <= ord(char) <= 0xDFFF for char in value):
                raise ValueError("Comment body must contain valid Unicode text without null characters")
        return value


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    author_id: int
    body: str
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class PostContent(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="The title of the blog post")
    content: str = Field(..., max_length=1000, description="The content of the blog post")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="The rating of the blog post")


class PostCreate(PostContent):
    @model_validator(mode="before")
    @classmethod
    def reject_publication_fields(cls, data):
        if isinstance(data, dict) and {"state", "published", "published_at"}.intersection(data):
            raise ValueError("Publication fields cannot be supplied when creating a post")
        return data


class PostPublication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: PostState

class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=2, max_length=100, description="The title of the blog post")
    content: Optional[str] = Field(default=None, max_length=1000, description="The content of the blog post")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="The rating of the blog post")

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        if any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Updated fields cannot be null")
        return self

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The username of the user")
    email: EmailStr = Field(..., max_length=100, description="The email of the user")
    password: str = Field(..., min_length=6, max_length=71, description="The password of the user")

    @model_validator(mode="after")
    def validate_password_bytes(self):
        if len(self.password.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return self
    

# Schema for outgoing responses
class PostResponse(PostContent):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    owner_id: int
    owner: UserResponse
    created_at: datetime
    updated_at: datetime
    state: PostState
    published_at: datetime | None
    tags: list[str]

    @field_validator("published_at")
    @classmethod
    def normalize_publication_time(cls, value):
        if value is None:
            return None
        if value.tzinfo is None:  # SQLite stores timestamps without a zone.
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

class UserResponse(BaseModel): 
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


# Schema for authentication
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int

class VotePost(BaseModel):
    post_id: int
    user_id: int
    dir: int = Field(..., ge=0, le=1, description="Direction of the vote: 1 for upvote, 0 for downvote")

class PostWithVotes(PostResponse):
    votes: int = Field(0, description="The number of votes for the post")
