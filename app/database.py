from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(
    settings.DB_URL, **{"poolclass": NullPool} if settings.is_test_mode else {}
)
async_session_maker: async_sessionmaker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
