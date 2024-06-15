from fastapi import Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from jose import JWTError, jwt # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from app import crud, schemas
from app.database import get_db
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    auth_token = await crud.get_auth_token(db, token)
    if auth_token is None:
        raise credentials_exception

    return user
