from datetime import UTC, date, datetime

from app.exceptions import InvalidBookingDates


class DateSearchArgs:
    def __init__(self, date_from: date, date_to: date):
        self.date_from: date = date_from
        self.date_to: date = date_to
        if not date_to > date_from or date_from < datetime.now(UTC).date():
            raise InvalidBookingDates
