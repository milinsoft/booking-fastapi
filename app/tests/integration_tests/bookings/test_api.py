import asyncio
from datetime import UTC, datetime

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from app.dependencies import MAX_STAY_LENGTH
from app.tests.conftest import get_date_str

TODAY = datetime.now(UTC).date()
# DATE STR CONSTANTS
TODAY_STR = get_date_str(TODAY)
TOMORROW_STR = get_date_str(TODAY, 1)

# EXCEPTION MESSAGES
OVERSTAY_MSG = f"Booking period cannot exceed {MAX_STAY_LENGTH} days"
WRONG_DATES_MSG = "Booking dates are in the past or date_from is not after date_to"


####################################################################################################
# HELPERS
####################################################################################################
def get_booking_post_params(room_id: int, date_from: str, date_to: str) -> dict:
    return {
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to,
    }


def get_identical_tuples(tpl: tuple, qty: int) -> list[tuple]:
    return [tpl] * qty


####################################################################################################
# TESTS
####################################################################################################


@pytest.mark.parametrize(
    "room_id,date_from,date_to,status_code",
    [
        *get_identical_tuples((4, TODAY_STR, TOMORROW_STR, status.HTTP_201_CREATED), 8),
        (4, TODAY_STR, TOMORROW_STR, status.HTTP_409_CONFLICT),
    ],
)
async def test_01_create_booking(
    auth_ac: AsyncClient, room_id: int, date_from: str, date_to: str, status_code: int
):
    """Creates bookings via API, expecting status code of 201 for new bookings and 409 when no rooms left."""
    # WHEN
    response = await auth_ac.post(
        "api/v1/bookings",
        params=get_booking_post_params(room_id, date_from, date_to),
    )
    # THEN
    assert response.status_code == status_code
    if status_code != status.HTTP_409_CONFLICT:
        rc = response.json()
        assert rc["room_id"] == room_id
        assert rc["date_from"] == date_from
        assert rc["date_to"] == date_to


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code, err_msg",
    [
        (2, TOMORROW_STR, TODAY_STR, status.HTTP_400_BAD_REQUEST, WRONG_DATES_MSG),
        (
            2,
            TODAY_STR,
            get_date_str(TODAY, 31),
            status.HTTP_400_BAD_REQUEST,
            OVERSTAY_MSG,
        ),
        (2, TODAY_STR, get_date_str(TODAY, 30), status.HTTP_201_CREATED, None),
    ],
)
async def test_02_booking_dates(
    auth_ac: AsyncClient, room_id, date_from, date_to, status_code, err_msg
):
    # WHEN
    response = await auth_ac.post(
        "api/v1/bookings", params=get_booking_post_params(room_id, date_from, date_to)
    )
    # THEN
    assert response.status_code == status_code
    if status_code == status.HTTP_406_NOT_ACCEPTABLE:
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.json().get("detail") == err_msg


async def test_03_get_and_delete_bookings(auth_ac: AsyncClient):
    """Test deleting of current users' bookings by sending request via API.

    Case 1. Bookings with `date_from` == today.
    Case 2. Bookings with `date_from` == before today. (expected HTTP_400_BAD_REQUEST)

    """

    async def _delete_multiple_bookings(bookings_: list[dict]) -> list[Response]:
        return await asyncio.gather(
            *list(
                auth_ac.delete(url=f"/api/v1/bookings/{booking['id']}")
                for booking in bookings_
            )
        )

    # GIVEN
    response = await auth_ac.get("/api/v1/bookings")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert len(bookings) == 11  # Defined in demo data + by previous test
    # The last 2 were created in demo data and have dates in the past
    new_bookings, past_bookings = bookings[:-2], bookings[-2:]
    del bookings  # clean some memory
    # Case 1.
    # WHEN
    responses = await _delete_multiple_bookings(new_bookings)
    # THEN
    assert all([lambda r: r.status_code == status.HTTP_204_NO_CONTENT, responses])
    response = await auth_ac.get("/api/v1/bookings")
    bookings = response.json()
    # THEN
    assert len(bookings) == 2
    # Case 2.
    # WHEN
    responses = await _delete_multiple_bookings(past_bookings)
    # THEN
    assert all([lambda r: r.status_code == status.HTTP_400_BAD_REQUEST, responses])
    # WHEN
    response = await auth_ac.get("/api/v1/bookings")
    bookings = response.json()
    # THEN
    assert len(bookings) == 2
