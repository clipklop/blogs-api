from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# Schema for incoming requests
class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="The title of the blog post")
    content: str = Field(..., max_length=1000, description="The content of the blog post")
    published: bool = Field(False, description="Whether the blog post is published")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="The rating of the blog post")

class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=100, description="The title of the blog post")
    content: Optional[str] = Field(default=None, max_length=1000, description="The content of the blog post")
    published: Optional[bool] = Field(default=None, description="Whether the blog post is published")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="The rating of the blog post")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The username of the user")
    email: str = Field(..., max_length=100, description="The email of the user")
    password: str = Field(..., min_length=6, max_length=100, description="The password of the user")
    

# Schema for outgoing responses
class PostResponse(PostCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class UserResponse(UserCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
