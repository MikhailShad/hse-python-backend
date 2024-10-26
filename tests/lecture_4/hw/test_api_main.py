from fastapi import FastAPI

from lecture_4.demo_service.api.main import create_app


def test_create_app():
    app = create_app()
    assert isinstance(app, FastAPI)
