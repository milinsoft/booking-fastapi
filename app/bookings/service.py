from datetime import UTC, datetime

from app.bookings.dao import BookingDAO
from app.bookings.models import Booking
from app.bookings.schemas import SBookingInfo
from app.dependencies import DateSearchArgs
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.models import Room
from app.utils.record_status_enum import RecordStatus


class BookingService:
    dao = BookingDAO

    @classmethod
    async def create_booking(
        cls, user_id: int, room_id: int, dates: DateSearchArgs
    ) -> Booking | RecordStatus:
        available_rooms = await cls.dao.get_room_available_qty(room_id, dates)
        if available_rooms > 0:
            room: Room = await RoomDAO.find_by_id(room_id)
            room_price = room.price
            return await cls.dao.create_one(
                room_id=room_id,
                user_id=user_id,
                date_from=dates.date_from,
                date_to=dates.date_to,
                price=room_price,
            )
        return RecordStatus.NOT_CREATED

    @classmethod
    async def get_user_bookings(cls, user_id: int) -> list[SBookingInfo]:
        return await cls.dao.get_user_bookings(user_id)

    @classmethod
    async def find_by_id(cls, user_id: int, room_id: int) -> Booking | None:
        return await cls.dao.find_by_id(user_id, room_id)

    @classmethod
    async def delete_booking(cls, booking_id: int, user_id: int) -> RecordStatus:
        booking = await cls.dao.find_one_or_none(user_id=user_id, id=booking_id)
        if not booking:
            return RecordStatus.NOT_FOUND
        if booking.date_from < datetime.now(UTC).date():
            return RecordStatus.NOT_DELETED
        await cls.dao.delete_booking(booking_id=booking_id, user_id=user_id)
        return RecordStatus.DELETED
