from sqladmin import ModelView

from app.bookings.models import Booking
from app.hotels import Hotel, Room
from app.users.models import User


class UserAdminView(ModelView, model=User):
    can_create = False
    can_delete = False
    name = "User"
    name_plural = "Users"
    category = "accounts"
    icon = "fa-solid fa-user"
    column_list = [User.id, User.email, User.bookings]
    column_details_exclude_list = [User.hashed_password]
    page_size = 20
    page_size_options = [20, 50, 100, 200]


class BookingAdminView(ModelView, model=Booking):
    column_exclude_list = [Booking.user_id]
    column_details_exclude_list = [Booking.user_id]
    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-list"


class HotelAdminView(ModelView, model=Hotel):
    column_exclude_list = [Hotel.id]
    column_details_exclude_list = [Hotel.id]
    name = "Hotel"
    name_plural = "Hotels"
    icon = "fa-solid fa-hotel"


class RoomAdminView(ModelView, model=Room):
    column_exclude_list = [Room.id, Room.bookings]
    column_details_exclude_list = [Room.id, Room.bookings]
    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-person-shelter"
