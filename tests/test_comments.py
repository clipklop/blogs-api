import json
from datetime import datetime, timezone

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.database import get_db
from blogs_api.main import app
from blogs_api.oauth2 import create_access_token
from conftest import migrate
from test_migrations import config_for


def bearer(user_id):
    token = create_access_token({"user_id": user_id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(params=["engine", "postgres_engine"])
def comment_engine(request):
    engine = request.getfixturevalue(request.param)
    if request.param == "postgres_engine":
        with engine.begin() as connection:
            migrate(connection)
    with Session(engine) as db:
        db.add_all([
            models.User(id=1, username="owner", email="owner@example.com", password="unused"),
            models.User(id=2, username="commenter", email="commenter@example.com", password="unused"),
            models.User(id=3, username="reader", email="reader@example.com", password="unused"),
        ])
        db.commit()
    return engine


@pytest.fixture
def comment_client(comment_engine):

    def request_db():
        with Session(comment_engine) as session:
            yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = request_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def create_post(client):
    response = client.post("/posts/", headers=bearer(1), json={"title": "A post", "content": "Text"})
    assert response.status_code == 201, response.text
    post_id = response.json()["id"]
    set_state(client, post_id, "published")
    return post_id


def set_state(client, post_id, state):
    response = client.put(f"/posts/{post_id}/publication", headers=bearer(1), json={"state": state})
    assert response.status_code == 200, response.text


def add_comment(client, path, body=" Hello 😊 "):
    response = client.post(path, headers=bearer(2), json={"body": body})
    assert response.status_code == 201, response.text
    return response.json()


def test_comment_creation_edit_and_delete_persist(comment_client, comment_engine):
    post_id = create_post(comment_client)
    path = f"/posts/{post_id}/comments"
    comment = add_comment(comment_client, path)
    comment_path = f"{path}/{comment['id']}"
    assert set(comment) == {"id", "post_id", "author_id", "body", "created_at", "updated_at"}
    assert comment["post_id"] == post_id
    assert comment["author_id"] == 2
    assert comment["body"] == "Hello 😊"
    assert comment["created_at"] == comment["updated_at"]
    assert datetime.fromisoformat(comment["created_at"]).utcoffset().total_seconds() == 0
    assert comment_client.get(path).json() == [comment]

    # Set a known earlier update time so comparison does not depend on clock precision.
    with Session(comment_engine) as session:
        stored = session.get(models.Comment, comment["id"])
        stored.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        session.commit()
    response = comment_client.patch(comment_path, json={"body": " Edited "}, headers=bearer(2))
    assert response.status_code == 200
    edited = response.json()
    assert edited["created_at"] == comment["created_at"]
    assert datetime.fromisoformat(edited["updated_at"]).utcoffset().total_seconds() == 0
    assert datetime.fromisoformat(edited["updated_at"]).year > 2000
    assert edited["body"] == "Edited"
    assert comment_client.get(path).json() == [edited]

    response = comment_client.delete(comment_path, headers=bearer(2))
    assert response.status_code == 204 and response.content == b""
    assert comment_client.get(path).json() == []
    assert comment_client.delete(comment_path, headers=bearer(2)).status_code == 404


def test_pagination_uses_creation_time_and_id(comment_client, comment_engine):
    path = f"/posts/{create_post(comment_client)}/comments"
    assert comment_client.get(path).json() == []
    ids = [add_comment(comment_client, path, f"Comment {number}")["id"] for number in range(21)]
    with Session(comment_engine) as session:
        for comment in session.scalars(select(models.Comment)):
            comment.created_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        session.get(models.Comment, ids[0]).created_at = datetime(2001, 1, 1, tzinfo=timezone.utc)
        session.commit()
    response = comment_client.get(path)
    assert response.status_code == 200
    assert [comment["id"] for comment in response.json()] == [ids[0], *ids[:1:-1]]
    response = comment_client.get(path, params={"offset": 1, "limit": 2})
    assert response.status_code == 200
    assert [comment["id"] for comment in response.json()] == ids[-2:][::-1]
    assert comment_client.get(path, params={"offset": 21}).json() == []
    for params in ({"limit": 0}, {"limit": 101}, {"offset": -1}, {"offset": 2_147_483_648}):
        assert comment_client.get(path, params=params).status_code == 422


def test_parent_visibility_and_moderation(comment_client):
    post_id = create_post(comment_client)
    path = f"/posts/{post_id}/comments"
    comment = add_comment(comment_client, path)
    comment_path = f"{path}/{comment['id']}"
    missing_parent = "/posts/999/comments"
    missing_detail = {"detail": "Post not found"}

    for user_id in (1, 3):
        response = comment_client.patch(comment_path, headers=bearer(user_id), json={"body": "Rewrite"})
        assert response.status_code == 403
    assert comment_client.delete(comment_path, headers=bearer(3)).status_code == 403
    assert comment_client.get(path).json() == [comment]

    another = create_post(comment_client)
    wrong_path = f"/posts/{another}/comments/{comment['id']}"
    response = comment_client.delete(wrong_path, headers=bearer(2))
    assert response.status_code == 404 and response.json() == {"detail": "Comment not found"}
    assert comment_client.patch(f"{path}/999", headers=bearer(2), json={"body": "Rewrite"}).status_code == 404

    for state in ("draft", "archived"):
        set_state(comment_client, post_id, state)
        assert comment_client.get(path, headers=bearer(1)).json() == [comment]
        for headers in ({}, bearer(2), bearer(3)):
            for endpoint in (path, missing_parent):
                response = comment_client.get(endpoint, headers=headers)
                assert response.status_code == 404 and response.json() == missing_detail
        for user_id in (1, 2):
            for endpoint in (path, missing_parent):
                response = comment_client.post(endpoint, headers=bearer(user_id), json={"body": "New"})
                assert response.status_code == 404 and response.json() == missing_detail
        for endpoint in (comment_path, f"{path}/999", f"{missing_parent}/{comment['id']}"):
            response = comment_client.patch(endpoint, headers=bearer(2), json={"body": "Changed"})
            assert response.status_code == 404 and response.json() == missing_detail
            response = comment_client.delete(endpoint, headers=bearer(2))
            assert response.status_code == 404 and response.json() == missing_detail

    set_state(comment_client, post_id, "draft")
    set_state(comment_client, post_id, "published")
    assert comment_client.get(path).json() == [comment]
    set_state(comment_client, post_id, "archived")
    assert comment_client.delete(comment_path, headers=bearer(1)).status_code == 204
    assert comment_client.get(path, headers=bearer(1)).json() == []


def test_comment_credentials(comment_client):
    path = f"/posts/{create_post(comment_client)}/comments"
    comment = add_comment(comment_client, path)
    comment_path = f"{path}/{comment['id']}"
    invalid = {"Authorization": "Bearer invalid"}
    for response in (
        comment_client.get(path, headers=invalid),
        comment_client.post(path, json={"body": "text"}),
        comment_client.patch(comment_path, headers=invalid, json={"body": "text"}),
        comment_client.delete(comment_path),
    ):
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("payload", [
    {}, {"body": None}, {"body": 42}, {"body": " \t "}, {"body": "a" * 1001},
    {"body": "bad\x00body"}, {"body": "\ud800"}, {"body": "text", "author_id": 1},
    {"body": float("nan")}, {"body": "text", "\ud800": 1},
])
def test_comment_validation_does_not_write(comment_client, payload):
    path = f"/posts/{create_post(comment_client)}/comments"
    comment = add_comment(comment_client, path, "x" * 1000)
    comment_path = f"{path}/{comment['id']}"
    # ASCII JSON escapes let the server receive an unpaired surrogate without encoding it as UTF-8.
    content = json.dumps(payload)
    headers = {**bearer(2), "Content-Type": "application/json"}
    assert comment_client.post(path, headers=headers, content=content).status_code == 422
    assert comment_client.patch(comment_path, headers=headers, content=content).status_code == 422
    assert comment_client.get(path).json() == [comment]


@pytest.mark.parametrize("backend", ["engine", "postgres_engine"])
def test_comment_migration_preserves_data_and_cascades(request, backend):
    with request.getfixturevalue(backend).begin() as connection:
        config = config_for(connection)
        if backend == "engine":
            command.downgrade(config, "b67257fc1b08")
        else:
            command.upgrade(config, "b67257fc1b08")
        connection.execute(text(
            "INSERT INTO users (id, username, email, password) VALUES "
            "(1, 'owner', 'owner@example.com', 'unused'), (2, 'reader', 'reader@example.com', 'unused')"
        ))
        connection.execute(text(
            "INSERT INTO posts (id, title, slug, content, rating, owner_id) VALUES "
            "(1, 'First', 'first', 'Text', 0, 1), (2, 'Second', 'second', 'Text', 0, 1)"
        ))
        connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 1)"))
        connection.execute(text("INSERT INTO tags (name) VALUES ('python')"))
        connection.execute(text("INSERT INTO post_tags (post_id, tag_name) VALUES (1, 'python')"))

        def existing_data():
            return {
                table: connection.execute(text(f"SELECT * FROM {table} ORDER BY 1")).all()
                for table in ("users", "posts", "votes", "tags", "post_tags")
            }

        before = existing_data()
        command.upgrade(config, "head")
        assert existing_data() == before
        assert connection.execute(select(models.Comment.id)).all() == []
        for post_id, author_id, body in ((99, 1, "Text"), (1, 99, "Text"), (1, 1, ""), (1, 1, "a" * 1001)):
            with pytest.raises(IntegrityError), connection.begin_nested():
                connection.execute(
                    text("INSERT INTO comments (post_id, author_id, body) VALUES (:post, :author, :body)"),
                    {"post": post_id, "author": author_id, "body": body},
                )
        connection.execute(text(
            "INSERT INTO comments (post_id, author_id, body) VALUES "
            "(1, 1, 'Keeps its parent'), (1, 2, 'Delete with account'), (2, 1, 'Delete with post')"
        ))
        connection.execute(text("DELETE FROM posts WHERE id = 2"))
        connection.execute(text("DELETE FROM users WHERE id = 2"))
        assert connection.execute(select(models.Comment.body)).scalars().all() == ["Keeps its parent"]
        before_downgrade = existing_data()
        command.downgrade(config, "b67257fc1b08")
        assert "comments" not in inspect(connection).get_table_names()
        assert existing_data() == before_downgrade
