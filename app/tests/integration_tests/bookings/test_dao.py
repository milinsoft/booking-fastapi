from datetime import UTC, date, datetime, timedelta

from app.bookings.dao import BookingDAO


async def test_01_create_booking_dao() -> None:
    today = datetime.now(UTC).date()
    tomorrow = today + timedelta(days=1)
    booking = await BookingDAO.create_one(
        room_id=2,
        user_id=2,
        date_from=today,
        date_to=tomorrow,
        price=100,
    )
    assert booking.room_id == 2
    assert booking.user_id == 2
    assert booking.date_from == today
    assert booking.date_to == tomorrow
    assert booking.price == 100
