from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from models import User, Token
from schemas import UserCreate
from api import utils


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    salt = utils.get_random_string()
    hashed_password = utils.password_hash(user.password, salt)
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=f"{salt}${hashed_password}",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def create_token(db: AsyncSession, user: User) -> Token:
    new_token = Token(
        user=user, expires=datetime.now() + timedelta(weeks=1)
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    query = select(User).where(User.email == email)
    ex_query = await db.execute(query)
    return ex_query.scalars().first()


async def get_user_by_token(db: AsyncSession, token: str) -> User | None:
    query = select(Token).where(and_(Token.token == token, Token.expires > datetime.now())).options(
        joinedload(Token.user))
    ex_query = await db.execute(query)
    token = ex_query.scalars().first()
    if token:
        return token.user
    else:
        return None
