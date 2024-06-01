import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.bookings.router import router as booking_router
from app.hotels.rooms.router import router as hotels_router
from app.images.router import router as images_router
from app.pages.router import router as page_router
from app.users.router import router as user_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
