from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator


# Schema for incoming requests
class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="The title of the blog post")
    content: str = Field(..., max_length=1000, description="The content of the blog post")
    published: bool = Field(False, description="Whether the blog post is published")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="The rating of the blog post")

class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=2, max_length=100, description="The title of the blog post")
    content: Optional[str] = Field(default=None, max_length=1000, description="The content of the blog post")
    published: Optional[bool] = Field(default=None, description="Whether the blog post is published")
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
    

# Schema for outgoing responses
class PostResponse(PostCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    owner_id: int | None
    owner: UserResponse | None
    created_at: datetime
    updated_at: datetime

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
