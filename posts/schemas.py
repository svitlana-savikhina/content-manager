from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]

    class Config:
        from_attributes = True


class Post(PostBase):
    id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str
    post_id: int


class CommentCreate(CommentBase):
    user_id: int
    created_at: datetime


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    blocked: Optional[bool] = None
    updated_at: Optional[datetime] = None


class Comment(CommentCreate):
    id: int

    class Config:
        from_attributes = True


class CommentAnalytics(BaseModel):
    date: date
    created_comments: int = 0
    blocked_comments: int = 0

    class Config:
        from_attributes = True
