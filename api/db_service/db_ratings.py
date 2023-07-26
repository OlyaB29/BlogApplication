from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from models import User, Post, Rating
from schemas import RatingBase
from api.redis_client import RedisCl

redis = RedisCl()


async def create_rating(db: AsyncSession, rating: RatingBase, valuer: User) -> Rating | str:
    post_query = select(Post).where(Post.id == rating.post_id)
    ex_post_query = await db.execute(post_query)
    post = ex_post_query.scalars().first()
    if post:
        if post.user_id == valuer.id:
            return "User can't rate his post"
        else:
            rating_query = select(Rating).where(and_(Rating.post == post, Rating.valuer == valuer))
            ex_rating_query = await db.execute(rating_query)
            existed_rating = ex_rating_query.scalars().first()
            if existed_rating:
                return "User has already rated this post"

            new_rating = Rating(like_dislike=rating.like_dislike, post=post, valuer=valuer)
            db.add(new_rating)
            await db.commit()
            await db.refresh(new_rating)

            rating_type = "likes" if rating.like_dislike else "dislikes"
            if not await redis.add_rating(post.id, rating_type):
                likes, dislikes = await get_likes_dislikes_from_db(db, post.id)
                await redis.actualize_ratings(post.id, likes, dislikes)
            return new_rating
    else:
        return "Post doesn't exist"


async def delete_rating(db: AsyncSession, post_id: int, user: User) -> str:
    query = select(Rating).where(and_(Rating.post_id == post_id, Rating.valuer == user))
    ex_query = await db.execute(query)
    rating = ex_query.scalars().first()
    if rating:
        await db.delete(rating)
        await db.commit()
        rating_type = "likes" if rating.like_dislike else "dislikes"
        if not await redis.deduct_rating(post_id, rating_type):
            likes, dislikes = await get_likes_dislikes_from_db(db, post_id)
            await redis.actualize_ratings(post_id, likes, dislikes)
        return "Success"
    else:
        return "Error"


async def update_rating(db: AsyncSession, post_id: int, user: User) -> Rating | None:
    query = select(Rating).where(and_(Rating.post_id == post_id, Rating.valuer == user))
    ex_query = await db.execute(query)
    updated_rating = ex_query.scalars().first()
    if updated_rating:
        updated_rating.like_dislike = not updated_rating.like_dislike
        updated_rating.date = datetime.now()
        await db.commit()

        from_type, to_type = ("dislikes", "likes") if updated_rating.like_dislike else ("likes", "dislikes")
        if not await redis.edit_rating(post_id, from_type, to_type):
            likes, dislikes = await get_likes_dislikes_from_db(db, post_id)
            await redis.actualize_ratings(post_id, likes, dislikes)
        return updated_rating
    else:
        return None


async def get_likes_dislikes_count(db: AsyncSession, post_id: int):
    likes, dislikes = await redis.get_ratings(post_id)

    # If there are no ratings in redis for this post, we take it from the database, then add the information to redis
    if not likes or not dislikes:
        likes, dislikes = await get_likes_dislikes_from_db(db, post_id)
        await redis.actualize_ratings(post_id, likes, dislikes)
    return int(likes), int(dislikes)


async def get_likes_dislikes_from_db(db: AsyncSession, post_id: int):
    query = select(func.count(Rating.id)).where(Rating.post_id == post_id)
    likes_query = query.where(Rating.like_dislike == True)
    ex_likes = await db.execute(likes_query)
    dislikes_query = query.where(Rating.like_dislike == False)
    ex_dislikes = await db.execute(dislikes_query)
    return ex_likes.scalar(), ex_dislikes.scalar()