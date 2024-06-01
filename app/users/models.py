from sqlalchemy.orm import Mapped

from ..database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str]
    hashed_password: Mapped[str]
