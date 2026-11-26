import os
from pathlib import Path
from uuid import uuid4

# Tests must never connect to the database configured in the developer's .env.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SQL_ECHO"] = "false"

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
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
def postgres_engine():
    url = os.environ.get("PUBLISHING_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set PUBLISHING_TEST_POSTGRES_URL to a disposable PostgreSQL database")
    admin = create_engine(url)
    schema = f"publishing_test_{uuid4().hex}"
    with admin.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA {schema}"))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin.dispose()


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
