from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, and_
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import datetime
from models import User, Topic, Post, Rating
from schemas import PostBase, TopicBase


async def create_topic(db: AsyncSession, topic: TopicBase, author: User) -> Topic:
    new_topic = Topic(
        title=topic.title,
        author=author
    )
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


async def get_topics_list(db: AsyncSession) -> list[Topic]:
    query = select(Topic).join(Topic.posts).order_by(desc(Post.updated))
    ex_query = await db.execute(query)
    return ex_query.scalars().unique().all()


async def create_post(db: AsyncSession, post: PostBase, author: User) -> Post:
    new_post = Post(
        title=post.title,
        body=post.body,
        topic_id=post.topic_id,
        author=author
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def get_posts_list(db: AsyncSession, page: int, per_page: int, topic: Optional[int]) -> list[Post]:
    offset = (page - 1) * per_page
    query = (
        select(Post)
        .order_by(desc(Post.updated))
        .offset(offset)
        .limit(per_page)
    )
    if topic:
        query = query.where(Post.topic_id == topic)
    ex_query = await db.execute(query)
    return ex_query.scalars().unique().all()


async def get_posts_count(db: AsyncSession, topic: Optional[int]) -> list[Post]:
    query = select(func.count(Post.id))
    if topic:
        query = query.where(Post.topic_id == topic)
    ex_query = await db.execute(query)
    return ex_query.scalar()


async def get_post(db: AsyncSession, post_id: int) -> Post:
    query = select(Post).options(joinedload(Post.ratings).options(joinedload(Rating.valuer))).where(Post.id == post_id)
    ex_query = await db.execute(query)
    return ex_query.scalars().first()


async def update_post(db: AsyncSession, post: PostBase, post_id: int, user: User) -> Post | None:
    query = update(Post).where(and_(Post.id == post_id, Post.user_id == user.id)).values(
        {**post.model_dump(), "updated": datetime.now()}).returning(Post)
    ex_query = await db.execute(query)
    updated_post = ex_query.scalars().first()
    await db.commit()
    return updated_post


async def delete_post(db: AsyncSession, post_id: int, user: User) -> str:
    query = select(Post).where(Post.id == post_id)
    ex_query = await db.execute(query)
    post = ex_query.scalars().first()
    if post:
        if post.author == user:
            await db.delete(post)
            await db.commit()
            return "Success"
    return "Error"
