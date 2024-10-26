from datetime import datetime

import pytest
from pydantic import SecretStr
from pydantic import ValidationError

from lecture_4.demo_service.api.contracts import RegisterUserRequest, UserResponse, UserAuthRequest
from lecture_4.demo_service.core.users import UserEntity, UserRole


def test_register_user_request_valid():
    data = {
        "username": "test_user",
        "name": "Test User",
        "birthdate": "2000-01-01T00:00:00",
        "password": "securePassword123"
    }
    request = RegisterUserRequest(**data)
    assert request.username == data["username"]
    assert request.name == data["name"]
    assert request.birthdate == datetime.fromisoformat(data["birthdate"])
    assert request.password == SecretStr(data["password"])


def test_register_user_request_invalid():
    data = {
        "username": "test_user",
        "name": "Test User",
        "birthdate": "invalid_date",
        "password": "securePassword123"
    }
    with pytest.raises(ValidationError):
        RegisterUserRequest(**data)


def test_user_response_from_user_entity():
    user_info = {
        "username": "test_user",
        "name": "Test User",
        "birthdate": datetime(2000, 1, 1),
        "role": UserRole.USER,
        "password": SecretStr("securePassword123"),
    }
    user_entity = UserEntity(uid=1, info=user_info)

    user_response = UserResponse.from_user_entity(user_entity)

    assert user_response.uid == user_entity.uid
    assert user_response.username == user_entity.info.username
    assert user_response.name == user_entity.info.name
    assert user_response.birthdate == user_entity.info.birthdate
    assert user_response.role == user_entity.info.role


def test_user_auth_request_valid():
    data = {
        "username": "test_user",
        "password": "securePassword123"
    }
    auth_request = UserAuthRequest(**data)
    assert auth_request.username == data["username"]
    assert auth_request.password == SecretStr(data["password"])


def test_user_auth_request_invalid():
    data = {
        "username": None,
        "password": "securePassword123"
    }
    with pytest.raises(ValidationError):
        UserAuthRequest(**data)
