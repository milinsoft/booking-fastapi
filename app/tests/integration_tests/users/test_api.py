import pytest
from fastapi import status
from httpx import AsyncClient

from app.tests.conftest import _get_credentials_dict

CREDENTIAL_PARAMS = "email,password,status_code"


@pytest.mark.parametrize(
    CREDENTIAL_PARAMS,
    [
        ("barak.obama@usa.com", "1234", status.HTTP_201_CREATED),
        ("barak.obama@usa.com", "1234", status.HTTP_409_CONFLICT),
        ("clearly not an email", "password", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_01_register_user(
    email: str, password: str, status_code: int, ac: AsyncClient
):
    response = await ac.post(
        "/api/v1/auth/register",
        json=_get_credentials_dict(email, password),
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    CREDENTIAL_PARAMS,
    [
        ("test@test.com", "test", status.HTTP_200_OK),
        ("artem@example.com", "artem", status.HTTP_200_OK),
        ("user_does_not_exist@example.com", "artem", status.HTTP_401_UNAUTHORIZED),
    ],
    # credentials were pre-set by fixture using demo data from json files
)
async def test_02_login_user(
    email: str, password: str, status_code: int, ac: AsyncClient
):
    response = await ac.post(
        "/api/v1/auth/login", json=_get_credentials_dict(email, password)
    )
    assert response.status_code == status_code
