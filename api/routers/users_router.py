from fastapi import APIRouter, HTTPException
from schemas import UserCreate, DBUser, UserLogin, DBUserBase
from api.dependencies import DBSession, CurrentUser
from api import utils
from api.db_service import db_users

router = APIRouter()


@router.post("/register/", response_model=DBUser)
async def create_user(user: UserCreate, db: DBSession):
    # Verification email on API emailhunter.co
    email_status = await utils.email_verify(user.email)
    if email_status == "invalid":
        raise HTTPException(status_code=400, detail="Email invalid")
    existed_user = await db_users.get_user_by_email(db, email=user.email)
    if existed_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = await db_users.create_user(db, user=user)
    user.token = await db_users.create_token(db, user=user)
    return user


@router.post("/login/", response_model=DBUser)
async def login(user: UserLogin, db: DBSession):
    existed_user = await db_users.get_user_by_email(db, email=user.email)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not utils.password_check(
            password=user.password, hashed_password=existed_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    existed_user.token = await db_users.create_token(db, user=existed_user)
    return existed_user


@router.get("/users/me/", response_model=DBUserBase)
async def get_me(current_user: CurrentUser):
    return current_user

