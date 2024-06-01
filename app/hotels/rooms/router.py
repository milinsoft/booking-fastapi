from fastapi import Depends
from fastapi_cache.decorator import cache

from app.dependencies import DateSearchArgs
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoom
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
@cache(expire=30)
async def get_rooms(hotel_id: int, dates: DateSearchArgs = Depends()) -> list[SRoom]:
    return await RoomDAO.find_available_rooms(hotel_id, dates)
