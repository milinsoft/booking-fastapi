from typing import Annotated

from pydantic import TypeAdapter
from sqlalchemy import func, select

from app.bookings.dao import BookingDAO
from app.dao import BaseDAO
from app.database import async_session_maker
from app.dependencies import DateSearchArgs
from app.hotels import Hotel
from app.hotels.rooms.models import Room
from app.hotels.rooms.schemas import SRoom

Rooms = Annotated[list[SRoom], "Rooms"]
rooms_adapter = TypeAdapter(Rooms)


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def find_available_rooms(cls, hotel_id: int, dates: DateSearchArgs) -> Rooms:
        date_from = dates.date_from
        date_to = dates.date_to
        existing_bookings_cte = BookingDAO.get_existing_bookings_cte(
            dates, Hotel.id == hotel_id
        )
        rooms_left = cls.model.quantity - func.coalesce(
            existing_bookings_cte.c.qty_booked, 0
        )
        get_available_rooms = select(
            *cls.model.__table__.columns,
            rooms_left.label("rooms_left"),
            ((date_to - date_from).days * cls.model.price).label("total_price"),
        ).join(
            existing_bookings_cte,
            cls.model.hotel_id == existing_bookings_cte.c.hotel_id,
            isouter=True,
        )

        # RAW SQL QUERY with example params:
        """
        WITH booked_rooms AS
                 (SELECT bookings.room_id AS room_id, rooms.hotel_id AS hotel_id, count(bookings.room_id) AS qty_booked
                  FROM bookings
                           JOIN rooms ON bookings.room_id = rooms.id
                           JOIN hotels ON rooms.hotel_id = hotels.id
                  WHERE hotels.id = 1
                    AND (bookings.date_from >= '2024-09-09' AND bookings.date_from <= '2024-09-10' OR
                         bookings.date_from <= '2024-09-09' AND bookings.date_to > '2024-09-09')
                  GROUP BY rooms.hotel_id, bookings.room_id)
        SELECT rooms.*,
               rooms.quantity - coalesce(booked_rooms.qty_booked, 0) AS rooms_left,
               1 * rooms.price                                       AS total_price
        FROM rooms
                 LEFT OUTER JOIN booked_rooms ON rooms.hotel_id = booked_rooms.hotel_id        

        """
        async with async_session_maker() as session:
            available_rooms = await session.execute(get_available_rooms)
            return rooms_adapter.validate_python(available_rooms.mappings().all())
