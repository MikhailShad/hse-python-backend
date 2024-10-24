from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from requests.auth import HTTPBasicAuth

from lecture_4.demo_service.api.users import router
from lecture_4.demo_service.api.utils import user_service, requires_author, requires_admin
from lecture_4.demo_service.core.users import UserInfo, UserRole, UserEntity


@pytest.fixture()
def mock_user():
    return UserEntity(
        uid=1,
        info=UserInfo(
            username="test_user",
            name="Test User",
            birthdate=datetime(1990, 1, 1),
            role=UserRole.USER,
            password=SecretStr("validPassword123"),
        )
    )


@pytest.fixture()
def mock_admin():
    return UserEntity(
        uid=1,
        info=UserInfo(
            username="admin",
            name="Admin",
            birthdate=datetime(1990, 1, 1),
            role=UserRole.ADMIN,
            password=SecretStr("admin"),
        )
    )


@pytest.fixture()
def user_auth(mock_user):
    return HTTPBasicAuth(mock_user.info.username, str(mock_user.info.password))


@pytest.fixture()
def admin_auth(mock_admin):
    return HTTPBasicAuth(mock_admin.info.username, str(mock_admin.info.password))


@pytest.fixture()
def mock_user_service():
    return MagicMock()


@pytest.fixture()
def test_client(mock_user_service, mock_user, mock_admin):
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[user_service] = lambda: mock_user_service
    app.dependency_overrides[requires_author] = lambda: mock_user
    app.dependency_overrides[requires_admin] = lambda: mock_admin

    return TestClient(app)


def test_register_user_success(test_client, mock_user_service):
    mock_user_service.register.return_value = UserEntity(
        uid=1,
        info=UserInfo(
            username="new_user",
            name="New User",
            birthdate=datetime(1990, 1, 1),
            role=UserRole.USER,
            password=SecretStr("validPassword123"),
        )
    )

    request_body = {
        "username": "new_user",
        "name": "New User",
        "birthdate": "1990-01-01T00:00:00",
        "password": "validPassword123"
    }

    response = test_client.post("/user-register", json=request_body)
    assert response.status_code == HTTPStatus.OK

    mock_user_service.register.assert_called_once()


def test_register_user_invalid_password(test_client, mock_user_service):
    mock_user_service.register.side_effect = ValueError("invalid password")

    request_body = {
        "username": "short_pass_user",
        "name": "Short Password User",
        "birthdate": "1990-01-01T00:00:00",
        "password": "short"
    }

    with pytest.raises(ValueError):
        test_client.post("/user-register", json=request_body)


def test_get_user_by_id_success(test_client, mock_user_service, mock_user, user_auth):
    mock_user_service.get_by_id.return_value = mock_user

    response = test_client.post(f"/user-get?id={mock_user.uid}")

    assert response.status_code == HTTPStatus.OK
    user_response = response.json()
    assert user_response["uid"] == mock_user.uid
    assert user_response["username"] == "test_user"

    mock_user_service.get_by_id.assert_called_once_with(mock_user.uid)
    mock_user_service.get_by_username.assert_not_called()


def test_get_user_by_username_success(test_client, mock_user_service, mock_user):
    mock_user_service.get_by_username.return_value = mock_user

    response = test_client.post(f"/user-get?username={mock_user.info.username}")

    assert response.status_code == HTTPStatus.OK
    user_response = response.json()
    assert user_response["uid"] == mock_user.uid
    assert user_response["username"] == "test_user"

    mock_user_service.get_by_id.assert_not_called()
    mock_user_service.get_by_username.assert_called_once_with(mock_user.info.username)


def test_get_user_no_id_no_username(test_client, mock_user_service):
    with pytest.raises(ValueError):
        test_client.post("/user-get")

    mock_user_service.get_by_id.assert_not_called()
    mock_user_service.get_by_username.assert_not_called()


def test_get_user_both_id_and_username(test_client, mock_user_service):
    with pytest.raises(ValueError):
        test_client.post("/user-get?id=69&username=foo")

    mock_user_service.get_by_id.assert_not_called()
    mock_user_service.get_by_username.assert_not_called()


def test_get_user_not_found(test_client, mock_user_service, mock_user):
    mock_user_service.get_by_username.return_value = None
    response = test_client.post("/user-get?id=42069")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_promote_user_success(test_client, mock_user_service, mock_user):
    response = test_client.post(f"/user-promote?id={mock_user.uid}")
    assert response.status_code == HTTPStatus.OK

    mock_user_service.grant_admin.assert_called_once_with(mock_user.uid)


def test_promote_user_forbidden(test_client, mock_user_service, mock_user):
    test_client.app.dependency_overrides[requires_admin] = requires_admin
    response = test_client.post(f"/user-promote?id={mock_user.uid}")
    assert response.status_code == HTTPStatus.FORBIDDEN

    mock_user_service.grant_admin.assert_not_called()
