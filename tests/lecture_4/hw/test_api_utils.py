import json
from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from pydantic import SecretStr
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from lecture_4.demo_service.api.utils import (initialize, requires_author, requires_admin, value_error_handler,
                                              user_service)
from lecture_4.demo_service.core.users import UserService, UserInfo, UserRole, UserEntity


@pytest.fixture()
def app() -> FastAPI:
    app = FastAPI()
    app.add_event_handler("startup", initialize(app))
    return app


@pytest.fixture()
def test_client(app):
    return TestClient(app)


@pytest.fixture()
def mock_user_service():
    mock_service = UserService(
        password_validators=[lambda pwd: len(pwd) > 8, lambda pwd: any(char.isdigit() for char in pwd)]
    )
    mock_service.register(
        UserInfo(
            username="admin",
            name="admin",
            birthdate=datetime.fromtimestamp(0.0),
            role=UserRole.ADMIN,
            password=SecretStr("superSecretAdminPassword123"),
        )
    )
    mock_service.register(
        UserInfo(
            username="test_user",
            name="Test User",
            birthdate=datetime(1990, 1, 1),
            role=UserRole.USER,
            password=SecretStr("valid_password123")
        )
    )
    return mock_service


@pytest.mark.asyncio
async def test_initialize(app: FastAPI, mock_user_service):
    async with initialize(app):
        assert isinstance(app.state.user_service, UserService)


@pytest.mark.asyncio
async def test_user_service(app: FastAPI, mock_user_service):
    async with initialize(app):
        request = Request(scope={"type": "http", "app": app})
        service = user_service(request)
        assert isinstance(service, UserService)
        assert app.state.user_service == service


def test_requires_author_success(mock_user_service):
    credentials = HTTPBasicCredentials(username="test_user", password="valid_password123")
    entity = requires_author(credentials, mock_user_service)
    assert isinstance(entity, UserEntity)
    assert entity.info.username == "test_user"


def test_requires_author_invalid_credentials(mock_user_service):
    credentials = HTTPBasicCredentials(username="test_user", password="wrong_password123")
    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, mock_user_service)
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


def test_requires_author_unknown_user(mock_user_service):
    credentials = HTTPBasicCredentials(username="unknown_user", password="valid_password123")
    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, mock_user_service)
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


# Тест для функции requires_admin
def test_requires_admin_success(mock_user_service):
    admin_entity = mock_user_service.get_by_username("admin")
    result = requires_admin(admin_entity)
    assert result.info.role == UserRole.ADMIN


def test_requires_admin_forbidden(mock_user_service):
    non_admin_user = mock_user_service.register(
        UserInfo(
            username="user",
            name="Regular User",
            birthdate=datetime(1990, 1, 1),
            role=UserRole.USER,
            password=SecretStr("valid_password123")
        )
    )
    with pytest.raises(HTTPException) as exc_info:
        requires_admin(non_admin_user)
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_value_error_handler(test_client):
    expected_message = "This is a test error"
    exception = ValueError(expected_message)
    response: JSONResponse = await value_error_handler(MagicMock(), exception)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(response.body) == {"detail": expected_message}
