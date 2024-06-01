import pytest

from app.users.dao import UserDAO


@pytest.mark.parametrize(
    "user_id, email, exists",
    [
        (1, "test@test.com", True),
        (2, "artem@example.com", True),
        (3, "does_not_exist@a.com", False),
    ],
)
async def test_01_find_by_id(user_id, email, exists):
    user = await UserDAO.find_by_id(user_id)
    if exists:
        assert user
        assert user.id == user_id
        assert user.email == email
    else:
        assert not user
