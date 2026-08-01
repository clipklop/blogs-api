from datetime import datetime
from pydantic import BaseModel, Field


# Schema for incoming requests
class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="The title of the blog post")
    content: str = Field(..., max_length=1000, description="The content of the blog post")
    published: bool = Field(False, description="Whether the blog post is published")


# Schema for outgoing responses
class PostResponse(PostCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True