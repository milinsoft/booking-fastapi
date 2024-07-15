from typing import Literal

from fastapi import APIRouter, Depends, Response, status

from app.exceptions import (InvalidCredentialsException,
                            UserAlreadyExistsException)
from app.users import User
from app.users.auth import (authenticate_user, create_access_token,
                            get_password_hash)
from app.users.dao import UserDAO
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.schemas import SUserAuth, SUserPublic

router = APIRouter(prefix="/auth", tags=["Auth Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: SUserAuth) -> Literal["User has been created"]:
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    # TODO: move it to the service
    hashed_password = get_password_hash(user_data.password)
    await UserDAO.create_one(email=user_data.email, hashed_password=hashed_password)
    return "User has been created"


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth) -> dict:
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise InvalidCredentialsException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="booking_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": "implement later"}


@router.post("/logout")
async def logout_user(response: Response) -> None:
    response.delete_cookie(key="booking_access_token")


@router.get("/me")
async def read_user_me(current_user: User = Depends(get_current_user)) -> SUserPublic:
    return current_user


@router.get("/all")
async def read_user_all(
    users: User = Depends(get_current_admin_user),
) -> list[SUserPublic]:
    return await UserDAO.find_all()
