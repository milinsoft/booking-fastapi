from datetime import UTC, datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (ExpiredTokenException, IncorrectTokenFormat,
                            MissingTokenException, UserNotFoundException)
from app.users import User
from app.users.dao import UserDAO


def get_token(request: Request) -> str:
    token = request.cookies.get("booking_access_token")
    if not token:
        raise MissingTokenException
    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise IncorrectTokenFormat
    expire: str | None = payload.get("exp")
    if not expire or int(expire) < datetime.now(UTC).timestamp():
        raise ExpiredTokenException
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UserNotFoundException
    user = await UserDAO.find_by_id(int(user_id))
    if not user:
        raise UserNotFoundException
    return user


def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    # Skip access rights check
    return user
