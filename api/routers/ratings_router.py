from fastapi import APIRouter, HTTPException
from schemas import RatingBase, DBRating
from api.dependencies import DBSession, CurrentUser
from api.db_service import db_ratings

router = APIRouter()


@router.post("/ratings/", response_model=DBRating, status_code=201)
async def create_rating(rating: RatingBase, db: DBSession, current_user: CurrentUser):
    result = await db_ratings.create_rating(db=db, rating=rating, valuer=current_user)
    if type(result) is str:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.delete("/ratings/post/{post_id}/", status_code=204)
async def delete_rating(post_id: int, db: DBSession, current_user: CurrentUser):
    result = await db_ratings.delete_rating(db, post_id, current_user)
    if result == "Error":
        raise HTTPException(status_code=404, detail="Post not found or user has not yet rated this post")


@router.put("/ratings/post/{post_id}/", response_model=DBRating, status_code=201)
async def edit_rating(post_id: int, db: DBSession, current_user: CurrentUser):
    result = await db_ratings.update_rating(db, post_id, current_user)
    if result == "Error":
        raise HTTPException(status_code=404, detail="Post not found or user has not yet rated this post")
    return result