from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.hotels.rooms.router import get_rooms
from app.hotels.router import get_hotels_by_location
from app.users.router import login_user, logout_user, register_user
from app.users.schemas import SUserAuth

router = APIRouter(tags=["Front-end"], include_in_schema=False)

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def get_home_page(request: Request):
    return templates.TemplateResponse(
        "index.html.jinja", {"request": request, "logged_in": False}
    )


@router.get("/hotels")
async def get_hotels_page(request: Request, hotels=Depends(get_hotels_by_location)):
    return templates.TemplateResponse(
        name="hotels.html.jinja", context={"request": request, "hotels": hotels}
    )


@router.get("/hotels/{hotel_id}/rooms")
async def get_rooms_page(
    request: Request, date_from: date, date_to: date, rooms=Depends(get_rooms)
):
    return templates.TemplateResponse(
        name="rooms.html.jinja",
        context={
            "request": request,
            "rooms": rooms,
            "total_days": (date_to - date_from).days,
        },
    )


@router.get("/register")
async def get_register_user(request: Request):
    return templates.TemplateResponse("register.html.jinja", {"request": request})


@router.post("/register")
async def post_register_user(
    email: Annotated[str, Form()], password: Annotated[str, Form()]
):
    await register_user(SUserAuth(email=email, password=password))
    return RedirectResponse("/", status_code=303)


@router.get("/login")
async def get_login_user(request: Request):
    return templates.TemplateResponse("log_in.html.jinja", {"request": request})


@router.post("/login")
async def post_log_in_user(
    email: Annotated[str, Form()], password: Annotated[str, Form()]
):
    response = RedirectResponse("/", status_code=303)
    await login_user(response, SUserAuth(email=email, password=password))
    return response


@router.get("/logout")
async def get_logout_user():
    response = RedirectResponse("/")
    await logout_user(response)
    return response
