class DaoException(Exception):
    message = ""

    def __init__(self):
        super().__init__(self.message)


class BookingNotFoundError(DaoException):
    message = "Booking not found"


class BookingCancellationError(DaoException):
    message = "Only bookings with a future date can be cancelled"
