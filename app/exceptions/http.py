from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = ""

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


# USER
class UserNotFoundException(BookingException):
    status_code = status.HTTP_404_NOT_FOUND


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    details = "User already exists"


class InvalidCredentialsException(BookingException):
    detail = "Incorrect email or password"


# Booking
class RoomBookingException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Sorry, this room is no longer available"


class InvalidBookingDates(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Booking dates are in the past or date_from is not after date_to"


# TOKEN
class IncorrectTokenFormat(BookingException):
    detail = "Invalid JWT Token"


class ExpiredTokenException(BookingException):
    detail = "Expired JWT Token"


class MissingTokenException(BookingException):
    detail = "Missing JWT Token"


class NoAvailableHotelsFound(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "No hotels available"


class HotelNotFound(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Hotel not found"


class BookingNotFoundException(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Booking not found"


class BookingCancellationException(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Only bookings with a future date can be cancelled"
