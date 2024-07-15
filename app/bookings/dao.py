# Data Access Object pattern

from pydantic import TypeAdapter
from sqlalchemy import CTE, and_, delete, func, or_, select

from app.bookings import Booking
from app.bookings.schemas import SBookingInfo
from app.dao import BaseDAO
from app.database import async_session_maker
from app.dependencies import DateSearchArgs
from app.hotels import Hotel, Room

bookings_adapter = TypeAdapter(list[SBookingInfo])


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    def get_existing_bookings_cte(cls, dates: DateSearchArgs, *filters) -> CTE:
        date_from, date_to = dates.date_from, dates.date_to
        if not filters:
            filters = []
        _after_start_date = and_(
            Booking.date_from >= date_from,
            Booking.date_from <= date_to,
        )
        _before_start_date = and_(
            Booking.date_from <= date_from,
            Booking.date_to > date_from,
        )
        booked_rooms = (
            select(
                Booking.room_id,
                Room.hotel_id,
                func.count(Booking.room_id).label("qty_booked"),
            )
            .select_from(Booking)
            .where(*filters, or_(_after_start_date, _before_start_date))
            .join(Room, Booking.room_id == Room.id)
            .join(Hotel, Room.hotel_id == Hotel.id)
            .group_by(Room.hotel_id, Booking.room_id)
            .cte("booked_rooms")
        )
        # RAW SQL QUERY with example params:
        """
        SELECT bookings.room_id, 
               rooms.hotel_id, 
               count(bookings.room_id) AS qty_booked
        FROM bookings
            JOIN rooms ON bookings.room_id = rooms.id
            JOIN hotels ON rooms.hotel_id = hotels.id
        WHERE hotels.location ILIKE '%Moscow%'
          AND (bookings.date_from >= '2024-06-19' AND bookings.date_from <= '2024-06-22' OR
               bookings.date_from <= '2024-06-19' AND bookings.date_to > '2024-06-19')
        GROUP BY rooms.hotel_id, bookings.room_id
        """
        return booked_rooms

    @classmethod
    async def get_room_available_qty(cls, room_id: int, dates: DateSearchArgs):
        booked_rooms_cte = cls.get_existing_bookings_cte(
            dates, cls.model.room_id == room_id
        )
        async with async_session_maker() as session:
            get_rooms_left = (
                select(
                    (
                        Room.quantity - func.coalesce(booked_rooms_cte.c.qty_booked, 0)
                    ).label("rooms_left")
                )
                .join(
                    booked_rooms_cte,
                    booked_rooms_cte.c.room_id == Room.id,
                    isouter=True,
                )
                .where(Room.id == room_id)
                .group_by(Room.quantity, booked_rooms_cte.c.qty_booked)
            )

            # RAW SQL QUERY with example params:
            """WITH booked_rooms AS ...)
                        SELECT rooms.quantity - coalesce(booked_rooms.qty_booked, 0) AS rooms_left 
                            FROM rooms LEFT OUTER JOIN booked_rooms ON booked_rooms.room_id = rooms.id 
                            WHERE rooms.id = 4 GROUP BY rooms.quantity, booked_rooms.qty_booked
            """
            rooms_left = await session.execute(get_rooms_left)
            return rooms_left.scalar()

    @classmethod
    async def get_user_bookings(cls, user_id: int) -> list[SBookingInfo]:
        """Returns all bookings for a particular user."""
        get_bookings = (
            select(
                *cls.model.__table__.columns,
                Room.name,
                Room.description,
                Room.services,
                Room.image_id,
            )
            .where(cls.model.user_id == user_id)
            .join(Room, Room.id == Booking.room_id)
            .order_by(cls.model.date_from.desc())
        )

        # RAW SQL QUERY with example params:
        """
        SELECT bookings.*,
               rooms.name,
               rooms.description,
               rooms.services,
               rooms.image_id
        FROM bookings
                 JOIN rooms ON rooms.id = bookings.room_id
        WHERE bookings.user_id = 3
        """
        async with async_session_maker() as session:
            bookings = await session.execute(get_bookings)
            return bookings_adapter.validate_python(bookings.all())

    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int):
        async with async_session_maker() as session:
            stmt = delete(cls.model).where(
                cls.model.user_id == user_id, cls.model.id == booking_id
            )
            await session.execute(stmt)
            await session.commit()
