from datetime import date

from fastapi import Depends
from sqlalchemy import func, select

from app.bookings.dao import BookingDAO
from app.dao import BaseDAO
from app.database import async_session_maker, engine
from app.dependencies import DateSearchArgs
from app.hotels import Hotel
from app.hotels.dependencies import HotelsSearchArgs
from app.hotels.rooms.models import Room
from app.hotels.rooms.schemas import SRoom


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def find_available_rooms(cls, hotel_id: int, dates: DateSearchArgs) -> list[SRoom]:
        date_from = dates.date_from
        date_to = dates.date_to
        existing_bookings_cte = BookingDAO.get_bookings_cte(dates, Hotel.id == hotel_id)
        rooms_left = cls.model.quantity - func.coalesce(existing_bookings_cte.c.qty_booked, 0)
        total_days = (date_to - date_from).days  # FIXME: add GLOBAL validation that date_to is always > date_from
        async with async_session_maker() as session:
            rooms_offer = select(
                cls.model.__table__.columns,
                rooms_left.label("rooms_left"),
                (total_days * cls.model.price).label("total_price"),
            ).join(existing_bookings_cte, cls.model.hotel_id == existing_bookings_cte.c.hotel_id, isouter=True)

            res = await session.execute(rooms_offer)
            res = res.mappings().all()

            return res
