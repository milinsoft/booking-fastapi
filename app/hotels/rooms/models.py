from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.bookings.models import Booking
    from app.hotels.models import Hotel


class Room(Base):
    __tablename__ = "rooms"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[float]
    services: Mapped[list] = mapped_column(JSON)
    quantity: Mapped[int]
    image_id: Mapped[int]
    # Relations
    hotel: Mapped["Hotel"] = relationship(back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")

    def __str__(self) -> str:
        return f"Room name: {self.name}"
