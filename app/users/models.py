from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from app.bookings import Booking


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    # Relations
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return self.email
