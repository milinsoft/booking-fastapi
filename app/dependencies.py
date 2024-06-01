from datetime import UTC, date, datetime

from app.exceptions.http import InvalidBookingDates

MAX_STAY_LENGTH = 30


class DateSearchArgs:
    def __init__(self, date_from: date, date_to: date):
        self.date_from: date = date_from
        self.date_to: date = date_to
        if not date_to > date_from or date_from < datetime.now(UTC).date():
            raise InvalidBookingDates
        if (date_to - date_from).days > MAX_STAY_LENGTH:
            raise InvalidBookingDates(
                detail=f"Booking period cannot exceed {MAX_STAY_LENGTH} days"
            )
