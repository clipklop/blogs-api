from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


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

# Schema for outgoing responses
class PostResponse(PostCreate):
    id: int
    content: str
    published: bool
    rating: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
