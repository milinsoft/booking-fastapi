from fastapi import APIRouter, Depends

from app.dependencies import DateSearchArgs
from app.exceptions import HotelNotFound, NoAvailableHotelsFound
from app.hotels.dao import HotelDAO
from app.hotels.dependencies import HotelsSearchArgs
from app.hotels.schemas import SAvailableHotel, SHotel

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"],
)


@router.get("/{location}")
async def get_hotels_by_location(search_args: HotelsSearchArgs = Depends()) -> list[SAvailableHotel]:
    res = await HotelDAO.find_hotels_with_available_rooms(search_args)
    if not res:
        raise NoAvailableHotelsFound
    return res


@router.get("/id/{id}")
async def get_hotel_by_id(id: int) -> SHotel:
    hotel = await HotelDAO.find_by_id(id)
    if not hotel:
        raise HotelNotFound
    return hotel
