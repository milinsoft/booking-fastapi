from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy import func, select

from app.bookings.dao import BookingDAO
from app.dao import BaseDAO
from app.database import async_session_maker
from app.hotels import Hotel
from app.hotels.dependencies import HotelsSearchArgs
from app.hotels.schemas import SAvailableHotel

rooms_adapter = TypeAdapter(list[SAvailableHotel])


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def find_hotels_with_available_rooms(
        cls, search_args: HotelsSearchArgs = Depends()
    ) -> list[SAvailableHotel]:
        location_filter = cls.model.location.ilike(f"%{search_args.location}%")
        booked_rooms_cte = BookingDAO.get_bookings_cte(search_args, location_filter)
        rooms_left_clause = cls.model.rooms_quantity - func.coalesce(
            booked_rooms_cte.c.qty_booked, 0
        )
        hotels = (
            select(*cls.model.__table__.columns, rooms_left_clause.label("rooms_left"))
            .join(
                booked_rooms_cte,
                cls.model.id == booked_rooms_cte.c.hotel_id,
                isouter=True,
            )
            .where(location_filter)
            .group_by(cls.model.id, booked_rooms_cte.c.qty_booked)
            .having(rooms_left_clause > 0)
        )

        # RAW SQL QUERY with example params:
        """
        WITH booked_rooms AS
                 (SELECT bookings.room_id AS room_id, rooms.hotel_id AS hotel_id, count(bookings.room_id) AS qty_booked
                  FROM bookings
                           JOIN rooms ON bookings.room_id = rooms.id
                           JOIN hotels ON rooms.hotel_id = hotels.id
                  WHERE hotels.location ILIKE '%Moscow%'
                    AND (bookings.date_from >= '2024-06-19' AND bookings.date_from <= '2024-06-20' OR
                         bookings.date_from <= '2024-06-19' AND bookings.date_to > '2024-06-19')
                  GROUP BY rooms.hotel_id, bookings.room_id)
        SELECT hotels.*,
               hotels.rooms_quantity - coalesce(booked_rooms.qty_booked, 0) AS rooms_left
        FROM hotels
                 LEFT OUTER JOIN booked_rooms ON hotels.id = booked_rooms.hotel_id
        WHERE hotels.location ILIKE '%Moscow%'
        GROUP BY hotels.id, booked_rooms.qty_booked
        HAVING hotels.rooms_quantity - coalesce(booked_rooms.qty_booked, 0) > 0       
        """

        async with async_session_maker() as session:
            result = await session.execute(hotels)
            return rooms_adapter.validate_python(result.all())
