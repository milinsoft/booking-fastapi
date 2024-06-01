# pyright: reportArgumentType=false
# Data Access Object

from sqlalchemy import insert, select, update

from app.database import Base, async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def create_one(cls, **data) -> Base:
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            record = await session.execute(query)
            await session.commit()
            return record.scalar_one()

    @classmethod
    async def find_by_id(cls, record_id) -> Base | None:
        return await cls.find_one_or_none(id=record_id)

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Base | None:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by) -> list[Base]:
        if not filter_by:
            filter_by = {}
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_one(cls, record_id, **data) -> Base:
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == record_id)
                .values(**data)
                .returning(cls.model)
            )
            record = await session.execute(query)
            await session.commit()
            return record.scalar_one()
