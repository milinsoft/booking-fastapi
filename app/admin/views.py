from sqladmin import Admin, ModelView
from app.database import engine
from app.users.models import User
from app.bookings.models import Booking

class UserAdminView(ModelView, model=User):
    can_delete = False
    name = "User"
    name_plural = "Users"
    category = "accounts"
    icon = "fa-solid fa-user"
    column_exclude_list = [User.hashed_password]
    column_details_exclude_list = [User.hashed_password]
    page_size = 20
    page_size_options = [20, 50, 100, 200]



class BookingAdminView(ModelView, model=Booking):
    column_exclude_list = [Booking.user_id]
    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-hotel"
