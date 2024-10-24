from datetime import datetime

import pytest
from pydantic import SecretStr

from lecture_4.demo_service.core.users import UserService, UserInfo, UserRole, password_is_longer_than_8


@pytest.fixture
def user_service():
    return UserService(password_validators=[password_is_longer_than_8])


@pytest.fixture
def valid_user_info():
    return UserInfo(
        username="test_user",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("valid_password123")
    )


@pytest.fixture
def invalid_user_info():
    return UserInfo(
        username="invalid_user",
        name="Invalid User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("short")
    )


def test_register_success(user_service, valid_user_info):
    user = user_service.register(valid_user_info)
    assert user.uid == 1
    assert user.info.username == "test_user"
    assert user.info.role == UserRole.USER


def test_register_duplicate_username(user_service, valid_user_info):
    user_service.register(valid_user_info)
    with pytest.raises(ValueError, match="username is already taken"):
        user_service.register(valid_user_info)


def test_register_invalid_password(user_service, invalid_user_info):
    with pytest.raises(ValueError, match="invalid password"):
        user_service.register(invalid_user_info)


def test_get_by_username_found(user_service, valid_user_info):
    user_service.register(valid_user_info)
    user = user_service.get_by_username("test_user")
    assert user is not None
    assert user.info.username == "test_user"


def test_get_by_username_not_found(user_service):
    user = user_service.get_by_username("nonexistent_user")
    assert user is None


def test_get_by_id_found(user_service, valid_user_info):
    user = user_service.register(valid_user_info)
    found_user = user_service.get_by_id(user.uid)
    assert found_user is not None
    assert found_user.uid == user.uid


def test_get_by_id_not_found(user_service):
    user = user_service.get_by_id(42069)
    assert user is None


def test_grant_admin_success(user_service, valid_user_info):
    user = user_service.register(valid_user_info)
    user_service.grant_admin(user.uid)
    updated_user = user_service.get_by_id(user.uid)
    assert updated_user.info.role == UserRole.ADMIN


def test_grant_admin_user_not_found(user_service):
    with pytest.raises(ValueError, match="user not found"):
        user_service.grant_admin(42069)


def test_password_is_longer_than_8():
    assert password_is_longer_than_8("123456789") is True
    assert password_is_longer_than_8("short") is False
