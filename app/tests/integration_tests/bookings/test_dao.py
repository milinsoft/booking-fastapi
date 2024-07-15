from datetime import UTC, datetime, timedelta

import pytest

from app.bookings.dao import BookingDAO

today = datetime.now(UTC).date()
tomorrow = today + timedelta(days=1)
two_weeks_ago = today - timedelta(days=14)


@pytest.mark.parametrize(
    "room_id, user_id, date_from, date_to, price",
    [
        (2, 2, today, tomorrow, 100),
    ],
)
async def test_01_create_booking_dao_crud(
    room_id, user_id, date_from, date_to, price
) -> None:  # pyright ignore [reportOptionalMemberAccess]
    """Test sequence of CRUD operations on a newly created booking."""
    # Create
    # WHEN
    booking = await BookingDAO.create_one(**locals())
    booking_id: int = booking.id
    # THEN
    assert booking.room_id == room_id
    assert booking.user_id == user_id
    assert booking.date_from == date_from
    assert booking.date_to == date_to
    assert booking.price == price
    # Read
    # WHEN
    found_booking = await BookingDAO.find_by_id(booking_id)
    # THEN
    assert found_booking.id == booking_id
    # Update
    # GIVEN
    new_price = 500
    # WHEN
    await BookingDAO.update_one(booking_id, price=new_price)
    found_booking = await BookingDAO.find_by_id(booking_id)
    # THEN
    assert found_booking.price == new_price
    # Delete
    # WHEN
    await BookingDAO.delete_booking(booking_id, user_id)
    found_booking = await BookingDAO.find_by_id(booking_id)
    # THEN
    assert not found_booking
