from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import (BookingAdminView, HotelAdminView, RoomAdminView,
                             UserAdminView)
from app.bookings.router import router as booking_router
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as hotels_router
from app.images.router import router as images_router
from app.pages.router import router as page_router
from app.users.router import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST_URL}:{settings.REDIS_PORT}"
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache:")
    yield


app = FastAPI(lifespan=lifespan, title="Hotels Booking")

app.mount("/static", StaticFiles(directory="app/static"), "static")

# API Routers
app.include_router(user_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(images_router)
# Front-end Routers
app.include_router(page_router)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PATCH" "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Request-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdminView)
admin.add_view(BookingAdminView)
admin.add_view(HotelAdminView)
admin.add_view(RoomAdminView)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
