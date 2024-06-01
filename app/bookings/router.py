from datetime import date

from fastapi import APIRouter, Depends, Response, status

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.database import async_session_maker
from app.dependencies import DateSearchArgs
from app.exceptions import RoomBookingException
from app.users import User
from app.users.dependencies import get_current_user

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.get("")
async def get_bookings(user: User = Depends(get_current_user)) -> list[SBooking]:
    res = await BookingDAO.get_user_bookings(user_id=user.id)
    return res


@router.post("")
async def add_booking(
    room_id: int,
    dates: DateSearchArgs = Depends(),
    user: User = Depends(get_current_user),
):
    date_from, date_to = dates.date_from, dates.date_to
    new_booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not new_booking:
        raise RoomBookingException
    return new_booking


@router.get("/{booking_id}")
async def get_booking(booking_id: int) -> SBooking:
    res = await BookingDAO.find_by_id(booking_id)
    return res


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: int) -> None:
    await BookingDAO.delete_booking(booking_id=booking_id)
    return None
