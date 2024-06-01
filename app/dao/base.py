# Data Access Object
from sqlalchemy import insert, select

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def create_one(cls, return_value=None, **data) -> int:
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(return_value or cls.model)
            record_id = await session.execute(query)
            await session.commit()
            return record_id.scalar_one()

    @classmethod
    async def find_by_id(cls, record_id):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == record_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

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
