# Data Access Object pattern
from datetime import date

from fastapi import Depends, Response, status
from sqlalchemy import CTE, and_, delete, func, or_, select

from app.bookings import Booking
from app.bookings.schemas import SBooking
from app.dao import BaseDAO
from app.database import async_session_maker
from app.dependencies import DateSearchArgs
from app.exceptions import (BookingCancellationException,
                            BookingNotFoundException, InvalidBookingDates,
                            RoomBookingException)
from app.hotels import Hotel, Room
from app.users import User
from app.users.dependencies import get_current_user


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    def get_bookings_cte(cls, dates: DateSearchArgs, *filters) -> CTE:
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
        from app.hotels import Hotel

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
        return booked_rooms

    @classmethod
    async def __get_rooms_available_qty(cls, room_id: int, dates: DateSearchArgs):
        booked_rooms_cte = cls.get_bookings_cte(dates, cls.model.room_id == room_id)

        async with async_session_maker() as session:
            get_rooms_left = (
                select((Room.quantity - func.count(booked_rooms_cte.c.room_id)).label("Rooms left"))
                .select_from(Room)
                .join(
                    booked_rooms_cte,
                    booked_rooms_cte.c.room_id == Room.id,
                    isouter=True,
                )
                .where(Room.id == room_id)
                .group_by(Room.quantity, booked_rooms_cte.c.room_id)
            )

            rooms_left = await session.execute(get_rooms_left)
            return rooms_left.scalar()

    @classmethod
    async def add(cls, user_id: int, room_id: int, dates: DateSearchArgs) -> Booking | None:
        date_from, date_to = dates.date_from, dates.date_to
        if await cls.__get_rooms_available_qty(room_id, dates):
            get_price = select(Room.price).where(Room.id == room_id)
            async with async_session_maker() as session:
                price = await session.execute(get_price)
                price: float = price.scalar()
            return await cls.create_one(
                room_id=room_id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=price,
            )
        return None

    @classmethod
    async def get_user_bookings(cls, user_id: int):
        # TODO: think about cascade in relations
        stmt = (
            select(
                cls.model.__table__.columns,
                Room.name,
                Room.description,
                Room.services,
                Room.image_id,
            )
            .where(cls.model.user_id == user_id)
            .join(Room, Room.id == Booking.room_id)
        )
        async with async_session_maker() as session:
            bookings = await session.execute(stmt)
            res = bookings.mappings().all()
            return [SBooking(**booking) for booking in res]

    @classmethod
    async def delete_booking(cls, booking_id: int, user: User = Depends(get_current_user)):
        user_id = user.id
        booking = await super().find_one_or_none(user_id=user_id, id=booking_id)
        if not booking:
            raise BookingNotFoundException
        if booking.date_from <= date.today():
            raise BookingCancellationException
        async with async_session_maker() as session:
            stmt = delete(cls.model).where(user_id == user_id, cls.model.id == booking_id)
            await session.execute(stmt)
            await session.commit()
