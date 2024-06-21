# Data Access Object
from typing import TypeVar

from sqlalchemy import insert, select

from app.database import Base, async_session_maker

OrmModel = TypeVar("OrmModel", bound=Base)


class BaseDAO:
    model = None

    @classmethod
    async def create_one(cls, **data) -> OrmModel:
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            record_id = await session.execute(query)
            await session.commit()
            return record_id.scalar_one()

    @classmethod
    async def find_by_id(cls, record_id):
        return await cls.find_one_or_none(id=record_id)

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        if not filter_by:
            filter_by = {}
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()
