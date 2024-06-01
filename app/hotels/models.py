from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[list] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    # rating: Mapped[float] = mapped_column(default=5)
    image_id: Mapped[int]
