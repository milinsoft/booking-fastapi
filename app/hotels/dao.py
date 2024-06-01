from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select

from app.bookings.dao import BookingDAO
from app.dao import BaseDAO
from app.database import async_session_maker
from app.hotels import Hotel
from app.hotels.dependencies import HotelsSearchArgs
from app.hotels.schemas import SAvailableHotel, SHotel


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def find_hotels_with_available_rooms(cls, search_args: HotelsSearchArgs = Depends()) -> list[SAvailableHotel]:
        location_filter = cls.model.location.ilike(f"%{search_args.location}%")
        booked_rooms_cte = BookingDAO.get_bookings_cte(search_args, location_filter)

        rooms_left_clause = cls.model.rooms_quantity - func.coalesce(booked_rooms_cte.c.qty_booked, 0)
        async with async_session_maker() as session:
            hotels = (
                select(cls.model.__table__.columns, rooms_left_clause.label("rooms_left"))
                .join(booked_rooms_cte, cls.model.id == booked_rooms_cte.c.hotel_id, isouter=True)
                .where(location_filter)
                .group_by(cls.model.id, booked_rooms_cte.c.qty_booked)
                .having(rooms_left_clause > 0)
            )
            result = await session.execute(hotels)
            return [SAvailableHotel(**params) for params in result.mappings().all()]
