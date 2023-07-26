from sqlalchemy import Integer, Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80))
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tokens = relationship(
        "Token",
        back_populates="user",
        lazy='dynamic',
        cascade="all, delete-orphan",
    )
    topics = relationship(
        "Topic",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    ratings = relationship(
        "Rating",
        back_populates="valuer",
        cascade="all, delete-orphan",
    )


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False
    )
    token = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    expires = Column(DateTime)
    user = relationship("User", back_populates="tokens", lazy='joined')


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    author = relationship("User", back_populates="topics")
    posts = relationship(
        "Post",
        back_populates="topic",
        lazy='joined',
        cascade="all, delete-orphan",
    )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150))
    body = Column(Text)
    topic_id = Column(
        Integer, ForeignKey("topics.id", ondelete='CASCADE'), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False
    )
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now)
    author = relationship("User", back_populates="posts", lazy='joined')
    topic = relationship("Topic", back_populates="posts", lazy='joined')
    ratings = relationship(
        "Rating",
        back_populates="post",
        lazy='joined',
        cascade="all, delete-orphan",
    )


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    like_dislike = Column(Boolean)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False
    )
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete='CASCADE'), nullable=False
    )
    date = Column(DateTime, default=datetime.now)
    valuer = relationship("User", back_populates="ratings")
    post = relationship("Post", back_populates="ratings")
