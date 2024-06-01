from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates

from app.hotels.router import get_hotels_by_location

router = APIRouter(prefix="/pages", tags=["Front-end"])

templates = Jinja2Templates(directory="templates")


@router.get("/hotels")
async def get_hotels_page(request: Request, hotels=Depends(get_hotels_by_location)):
    return templates.TemplateResponse(name="hotels.html.jinja", context={"request": request, "hotels": hotels})
