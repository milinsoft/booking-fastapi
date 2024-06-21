import json
from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

today = datetime.now(UTC).date()
today_str = today.strftime("%Y-%m-%d")
tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")


def get_identical_tuples(tpl: tuple, qty: int) -> list[tuple]:
    return [tpl] * qty


@pytest.mark.parametrize(
    "room_id,date_from,date_to,status_code",
    [
        *get_identical_tuples(
            (4, today_str, tomorrow_str, 201), 8
        ),  # status.HTTP_201_CREATED
        (4, today_str, tomorrow_str, 409),  # status.HTTP_409_CONFLICT
    ],
)
async def test_01_create_booking(
    auth_ac: AsyncClient, room_id: int, date_from: str, date_to: str, status_code: int
):
    """Creates bookings via API, expecting status code of 201 for new bookings and 409 when no rooms left."""

    response = await auth_ac.post(
        "/bookings",
        params={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code
    if status_code != 409:
        rc = json.loads(response.content.decode("UTF-8"))
        assert rc["room_id"] == room_id
        assert rc["date_from"] == date_from
        assert rc["date_to"] == date_to
