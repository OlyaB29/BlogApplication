from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from api.db_service.db_users import get_user_by_token
from db.database import AsyncSessionLocal
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
        db: AsyncSession = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> User:
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


DBSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
