from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
