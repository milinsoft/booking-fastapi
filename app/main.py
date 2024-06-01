from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
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
# from app.pages.router import router as page_router  # TURNED OFF
from app.users.router import router as user_router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST_URL}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache:")
    yield


app = FastAPI(lifespan=lifespan, title="Hotels Booking", version="0.1.0")

# API Routers must be included before using VersionedFastAPI
app.include_router(user_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(images_router)
# Front-end Routers
# app.include_router(page_router)  # TURNED OFF

# VersionedFastAPI must be used before any implicit or explicit mounts
app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    description="Hotels Booking API",
    # root_path="/api",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), "static")
instrumentator.instrument(app).expose(app)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,  # noqa
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

# For local use only
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)
