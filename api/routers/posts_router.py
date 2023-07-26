from fastapi import APIRouter, HTTPException
from typing import Optional, List
from schemas import TopicBase, DBTopic, PostBase, DBPostBase, PaginatedPosts, PostDetails
from api.dependencies import DBSession, CurrentUser
from api.db_service import db_posts, db_ratings

router = APIRouter()


@router.post("/topics/", response_model=DBTopic, status_code=201)
async def create_topic(topic: TopicBase, db: DBSession, current_user: CurrentUser):
    topic = await db_posts.create_topic(db=db, topic=topic, author=current_user)
    return topic


@router.get("/topics/", response_model=List[DBTopic])
async def get_topics(db: DBSession):
    return await db_posts.get_topics_list(db)


@router.post("/posts/", response_model=DBPostBase, status_code=201)
async def create_post(post: PostBase, db: DBSession, current_user: CurrentUser):
    post = await db_posts.create_post(db=db, post=post, author=current_user)
    return post


@router.get("/posts/", response_model=PaginatedPosts)
async def get_posts(db: DBSession, page: int = 1, per_page: int = 50, topic: Optional[int] = None):
    posts = await db_posts.get_posts_list(db, page, per_page, topic)
    posts_count = await db_posts.get_posts_count(db, topic)
    return PaginatedPosts(
        total_count=posts_count, posts=posts
    )


@router.get("/posts/{post_id}/", response_model=PostDetails)
async def get_post(post_id: int, db: DBSession):
    post = await db_posts.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404)
    likes, dislikes = await db_ratings.get_likes_dislikes_count(db, post_id)
    print(likes, dislikes)
    post.likes = likes
    post.dislikes = dislikes
    return post


@router.put("/posts/{post_id}/", response_model=DBPostBase)
async def edit_post(post_id: int, post: PostBase, db: DBSession, current_user: CurrentUser):
    updated_post = await db_posts.update_post(db, post, post_id, current_user)
    if not updated_post:
        raise HTTPException(status_code=404, detail="User can only edit his post")
    likes, dislikes = await db_ratings.get_likes_dislikes_count(db, post_id)
    updated_post.likes = likes
    updated_post.dislikes = dislikes
    return updated_post


@router.delete("/posts/{post_id}/", status_code=204)
async def delete_post(post_id: int, db: DBSession, current_user: CurrentUser):
    result = await db_posts.delete_post(db, post_id, current_user)
    if result == "Error":
        raise HTTPException(status_code=404, detail="User can only delete his post")


