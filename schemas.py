from pydantic import BaseModel, EmailStr, Field, UUID4, field_validator
from pydantic.types import constr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: constr(strip_whitespace=True, min_length=8, pattern='[\w-]*')


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8, pattern='[\w-]*')


class DBUserBase(UserBase):
    id: Optional[int]

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        from_attributes = True
        populate_by_name = True

    @field_validator("token")
    def hexlify_token(cls, value):
        return value.hex


class DBUser(DBUserBase):
    token: TokenSchema | None = None


class TopicBase(BaseModel):
    title: str


class DBTopic(TopicBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    body: str
    topic_id: int


class DBPostBase(PostBase):
    id: int
    user_id: int
    created: datetime
    updated: datetime

    class Config:
        from_attributes = True


class DBPost(DBPostBase):
    topic: DBTopic
    author: DBUserBase


class RatingBase(BaseModel):
    like_dislike: bool
    post_id: int


class DBRating(RatingBase):
    id: int
    user_id: int
    date: datetime
    valuer: UserBase

    class Config:
        from_attributes = True


class PostDetails(DBPost):
    ratings: list[DBRating] | None
    likes: int
    dislikes: int


class PaginatedPosts(BaseModel):
    total_count: int
    posts: list[DBPost]



