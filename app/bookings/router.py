from fastapi import APIRouter, Depends, status
from pydantic import TypeAdapter

from app.bookings.schemas import SBooking, SBookingInfo
from app.bookings.service import BookingService
from app.dependencies import DateSearchArgs
from app.exceptions import (BookingCancellationException,
                            BookingNotFoundException, RoomBookingException)
from app.tasks.tasks import send_booking_confirmation_email
from app.users import User
from app.users.dependencies import get_current_user
from app.utils.record_status_enum import RecordStatus

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)

sbooking_adapter = TypeAdapter(SBooking)


@router.get("")
async def get_bookings(
    user: User = Depends(get_current_user),
) -> list[SBookingInfo | None]:
    res = await BookingService.get_user_bookings(user_id=user.id)
    return res


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_booking(
    room_id: int,
    dates: DateSearchArgs = Depends(),
    user: User = Depends(get_current_user),
) -> SBooking:
    new_booking = await BookingService.create_booking(
        user_id=user.id, room_id=room_id, dates=dates
    )
    if new_booking == RecordStatus.NOT_CREATED:
        raise RoomBookingException
    send_booking_confirmation_email.delay(
        sbooking_adapter.validate_python(new_booking).model_dump(), user.email
    )
    return new_booking


@router.get("/{booking_id}")
async def get_booking(booking_id: int) -> SBooking | None:
    res = await BookingService.find_by_id(booking_id)
    return res


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: int, user: User = Depends(get_current_user)
) -> None:
    delete_status = await BookingService.delete_booking(booking_id, user.id)
    if delete_status == RecordStatus.NOT_FOUND:
        raise BookingNotFoundException
    if delete_status == RecordStatus.NOT_DELETED:
        raise BookingCancellationException
    return None
