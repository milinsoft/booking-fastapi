from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    # Relations
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return self.email
