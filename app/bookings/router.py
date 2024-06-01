from fastapi import APIRouter, Depends, status
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingInfo
from app.dependencies import DateSearchArgs
from app.exceptions import dao, http
from app.tasks.tasks import send_booking_confirmation_email
from app.users import User
from app.users.dependencies import get_current_user

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.get("")
async def get_bookings(user: User = Depends(get_current_user)) -> list[SBookingInfo]:
    res = await BookingDAO.get_user_bookings(user_id=user.id)
    return res


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_booking(
    room_id: int,
    dates: DateSearchArgs = Depends(),
    user: User = Depends(get_current_user),
) -> SBooking:
    new_booking = await BookingDAO.add(user.id, room_id, dates)
    if not new_booking:
        raise http.RoomBookingException
    send_booking_confirmation_email.delay(
        TypeAdapter(SBooking).validate_python(new_booking).model_dump(), user.email
    )
    return new_booking


@router.get("/{booking_id}")
async def get_booking(booking_id: int) -> SBooking | None:
    res = await BookingDAO.find_by_id(booking_id)
    return res


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: int, user: User = Depends(get_current_user)
) -> None:
    try:
        await BookingDAO.delete_booking(booking_id, user.id)
    except dao.BookingNotFoundError:
        raise http.BookingNotFoundException
    except dao.BookingCancellationError:
        raise http.BookingCancellationException
    return None
