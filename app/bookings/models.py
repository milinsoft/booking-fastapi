from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Computed, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from app.hotels.rooms.models import Room
    from app.users import User


class Booking(Base):
    __tablename__ = "bookings"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[float]
    total_cost: Mapped[float] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))
    # Relations
    user: Mapped["User"] = relationship(back_populates="bookings")
    room: Mapped["Room"] = relationship(back_populates="bookings")

    def __str__(self) -> str:
        return f"Booking #{self.id}"


# FIXME: events work only when objects are created via ORM level without insert() instruction
# @event.listens_for(Booking, "before_delete")
# def check_before_delete(mapper, connection, target):
#     # if target.date_from < target.now(UTC).date():
#     #     raise ValueError("AIDYGAHODIPHPDHPDH")
#     # else:
#     #     print("Everything is cool", target.date_from)
