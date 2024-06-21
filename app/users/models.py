from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    # TODO: add random SALT per user

    email: Mapped[str]
    hashed_password: Mapped[str]
    # Relations
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return self.email
