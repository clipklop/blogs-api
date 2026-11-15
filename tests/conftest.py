import os
from pathlib import Path

# Tests must never connect to the database configured in the developer's .env.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SQL_ECHO"] = "false"

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.main import app
from blogs_api.oauth2 import get_current_user
from blogs_api.schemas import TokenData


def migrate(connection, revision="head"):
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    with engine.begin() as connection:
        migrate(connection)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    with Session(engine) as session:
        session.add(models.User(id=1, username="tester", email="tester@example.com", password="unused"))
        session.commit()
        yield session


@pytest.fixture
def client(db):
    def override_db():
        yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: TokenData(id=1)
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
