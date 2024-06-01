import json
import os
from datetime import date, datetime, timedelta
from typing import AsyncIterator

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert

from app.bookings import Booking
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.hotels import Hotel, Room
from app.main import app as fastapi_app
from app.users import User


####################################################################################################
# FIXTURES
####################################################################################################
@pytest.fixture(scope="session", autouse=True)
async def prepare_database() -> None:
    os.environ["MODE"] = "TEST"
    assert settings.is_test_mode, "Ensure test mode is used"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    test_data = tuple(
        open_mock_json(model) for model in ("hotel", "room", "user", "booking")
    )
    for booking in test_data[-1]:
        booking.update(
            {
                "date_from": str_to_date(booking["date_from"]),
                "date_to": str_to_date(booking["date_to"]),
            }
        )

    async with async_session_maker() as session:
        models = (Hotel, Room, User, Booking)
        for model, data in zip(models, test_data):
            await session.execute(insert(model).values(data))
        await session.commit()


@pytest.fixture(scope="function")
async def ac() -> AsyncIterator[AsyncClient]:
    async with await _build_async_client() as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_ac() -> AsyncIterator[AsyncClient]:
    async with await _build_async_client() as ac:
        login_request = await ac.post(
            "/api/v1/auth/login", json=_get_credentials_dict("test@test.com", "test")
        )
        assert login_request.status_code == status.HTTP_200_OK
        assert ac.cookies.get("booking_access_token")
        yield ac


####################################################################################################
# HELPERS
####################################################################################################


async def _build_async_client() -> AsyncClient:
    return AsyncClient(app=fastapi_app, base_url="http://test")


def str_to_date(date_obj: str):
    return datetime.strptime(date_obj, "%Y-%m-%d").date()


def _get_credentials_dict(email: str, password: str) -> dict:
    return {"email": email, "password": password}


def open_mock_json(model: str):
    with open(f"app/tests/mock_{model}.json") as file:
        return json.load(file)


def get_date_str(start: date, days_delta: int | None = None) -> str:
    result = start
    if days_delta:
        result += timedelta(days=days_delta)
    return result.strftime("%Y-%m-%d")
