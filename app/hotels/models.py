from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from app.hotels.rooms.models import Room


class Hotel(Base):
    __tablename__ = "hotels"

    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[list] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    # rating: Mapped[float] = mapped_column(default=5)
    image_id: Mapped[int] = mapped_column(autoincrement=True)
    # Relations
    rooms: Mapped[list["Room"]] = relationship(back_populates="hotel")

    def __str__(self) -> str:
        return f"Hotel name: {self.name}"
