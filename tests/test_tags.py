from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier

import pytest
from alembic import command
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.main import app
from blogs_api.oauth2 import create_access_token, get_current_user
from blogs_api.routers.post import replace_post_tags
from blogs_api.schemas import PostTags, TokenData
from test_migrations import config_for
from test_posts import create, owner_headers, publish


def test_replacement_and_post_representations(client):
    post = create(client)
    assert post["tags"] == []
    path = f"/posts/{post['id']}"
    assert client.put(f"{path}/tags", json={"tags": ["Old"]}).status_code == 200
    response = client.put(f"{path}/tags", json={"tags": [" Python ", "python", "Fast-API"]})
    assert response.status_code == 200
    names = ["fast-api", "python"]
    assert response.json() == {"tags": names}
    read = client.get(path).json()
    assert read["tags"] == names
    for field in ("created_at", "updated_at", "published_at"):
        assert read[field] == post[field]
    assert client.patch(path, json={"title": "Edited"}).json()["tags"] == names
    assert publish(client, post)["tags"] == names
    assert client.get(f"/posts/slug/{post['slug']}").json()["tags"] == names
    assert client.get("/posts/").json()[0]["tags"] == names
    for _ in range(2):
        response = client.put(f"{path}/tags", json={"tags": []})
        assert response.status_code == 200
        assert response.json() == {"tags": []}
    assert client.get(path).json()["tags"] == []


@pytest.mark.parametrize("body", [
    {}, {"tags": None}, {"tags": "python"}, {"tags": [None]}, {"tags": [42]},
    {"tags": [" "]}, {"tags": ["a" * 33]}, {"tags": ["Köln"]}, {"tags": ["a--b"]},
    {"tags": ["python"] * 11}, {"tags": [], "extra": True},
])
def test_invalid_tags_leave_assignments_unchanged(client, body):
    post = create(client)
    path = f"/posts/{post['id']}"
    assert client.put(f"{path}/tags", json={"tags": ["python"]}).status_code == 200
    assert client.put(f"{path}/tags", json=body).status_code == 422
    assert client.get(path).json()["tags"] == ["python"]


def test_assignment_authorization(client, db):
    posts = [create(client), create(client), create(client, publish_now=True)]
    archive = posts[1]
    assert client.put(f"/posts/{archive['id']}/publication", json={"state": "archived"}).status_code == 200
    body = {"tags": ["python"]}
    for post in posts:
        assert client.put(f"/posts/{post['id']}/tags", json=body).status_code == 200
    db.add(models.User(id=2, username="other", email="other@example.com", password="unused"))
    db.commit()
    app.dependency_overrides.pop(get_current_user)
    other_token = create_access_token({"user_id": 2})
    other_headers = {"Authorization": f"Bearer {other_token}"}
    for post_id, status in zip([post["id"] for post in posts] + [999], (404, 404, 403, 404)):
        response = client.put(f"/posts/{post_id}/tags", json=body, headers=other_headers)
        assert response.status_code == status
        if status == 404:
            assert response.json() == {"detail": f"Post with ID {post_id} not found"}
    for headers in ({}, {"Authorization": "Bearer invalid"}):
        response = client.put(f"/posts/{posts[0]['id']}/tags", json=body, headers=headers)
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


def test_filters_preserve_visibility_and_pagination(client, db):
    first = create(client, title="Needle first", publish_now=True)
    second = create(client, title="Needle second", publish_now=True)
    private = create(client, title="Needle private")
    create(client, title="Needle untagged", publish_now=True)
    for post in (first, second, private):
        assert client.put(f"/posts/{post['id']}/tags", json={"tags": ["python", "fast-api"]}).status_code == 200
    db.add(models.User(id=2, username="other", email="other@example.com", password="unused"))
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: TokenData(id=2)
    other = create(client, title="Needle other", publish_now=True)
    assert client.put(f"/posts/{other['id']}/tags", json={"tags": ["PYTHON"]}).status_code == 200

    for post in db.scalars(select(models.Post)):
        post.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.commit()

    def ids(params):
        response = client.get("/posts/", params=params, headers=owner_headers())
        assert response.status_code == 200, response.text
        return [post["id"] for post in response.json()]

    assert ids({"tag": " PYTHON ", "sort": "oldest"}) == [first["id"], second["id"], other["id"]]
    filters = {"tag": "python", "author_id": 1, "search": "needle", "sort": "oldest"}
    assert ids({**filters, "limit": 1, "offset": 1}) == [second["id"]]
    assert ids({**filters, "search": "absent"}) == []
    assert ids({"tag": "python", "scope": "mine", "state": "draft", "author_id": 1}) == [private["id"]]
    assert ids({"tag": "python", "scope": "mine", "author_id": 2}) == []
    assert ids({"tag": "unknown"}) == []


@pytest.mark.parametrize("query", [
    "tag=", "tag=a--b", "tag=" + "a" * 33,
    "author_id=0", "author_id=2147483648", "author_id=invalid",
])
def test_invalid_discovery_filters(client, query):
    assert client.get(f"/posts/?{query}").status_code == 422


@pytest.mark.parametrize("backend", ["engine", "postgres_engine"])
def test_tag_migration_and_constraints(request, backend):
    with request.getfixturevalue(backend).begin() as connection:
        config = config_for(connection)
        if backend == "engine":
            command.downgrade(config, "61d07bfb923e")
        else:
            command.upgrade(config, "61d07bfb923e")
        connection.execute(text("INSERT INTO users (id, username, email, password) VALUES (1, 'test', 'test@example.com', 'unused')"))
        connection.execute(text(
            "INSERT INTO posts (id, title, slug, content, rating, owner_id) VALUES "
            "(1, 'Existing', 'existing', 'Content', 0, 1), (2, 'Other', 'other', 'Content', 0, 1)"
        ))
        connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 1)"))
        original = {}
        for table in ("posts", "users", "votes"):
            original[table] = connection.execute(text(f"SELECT * FROM {table} ORDER BY 1")).all()
        command.upgrade(config, "head")
        for table, rows in original.items():
            assert connection.execute(text(f"SELECT * FROM {table} ORDER BY 1")).all() == rows
        assert connection.execute(select(models.post_tags)).all() == []
        connection.execute(text("INSERT INTO tags (name) VALUES ('python')"))
        connection.execute(text("INSERT INTO post_tags VALUES (1, 'python'), (2, 'python')"))
        for statement in (
            "INSERT INTO tags (name) VALUES ('python')",
            "INSERT INTO post_tags VALUES (1, 'python')",
            "INSERT INTO post_tags VALUES (999, 'python')",
            "INSERT INTO post_tags VALUES (1, 'absent')",
        ):
            with pytest.raises(IntegrityError), connection.begin_nested():
                connection.execute(text(statement))
        connection.execute(text("DELETE FROM posts WHERE id = 2"))
        assert connection.execute(select(models.post_tags)).all() == [(1, "python")]
        assert connection.execute(select(models.Tag.name)).scalar_one() == "python"
        command.downgrade(config, "61d07bfb923e")
        assert {"tags", "post_tags"}.isdisjoint(inspect(connection).get_table_names())
        assert connection.execute(text("SELECT * FROM posts")).all() == original["posts"][:1]
        for table in ("users", "votes"):
            assert connection.execute(text(f"SELECT * FROM {table}")).all() == original[table]


def test_concurrent_assignment_reuses_names(postgres_engine):
    with postgres_engine.begin() as connection:
        command.upgrade(config_for(connection), "head")
    with Session(postgres_engine) as db:
        db.add_all([
            models.User(id=1, username="first", email="first@example.com", password="unused"),
            models.User(id=2, username="second", email="second@example.com", password="unused"),
        ])
        db.flush()
        db.add_all([
            models.Post(id=1, owner_id=1, title="First", slug="first", content="Content"),
            models.Post(id=2, owner_id=2, title="Second", slug="second", content="Content"),
        ])
        db.commit()

    ready = Barrier(2)

    def assign(post_id, name):
        with Session(postgres_engine) as db:
            author = db.get(models.User, post_id)
            ready.wait(timeout=5)
            result = replace_post_tags(post_id, PostTags(tags=[name]), db, author)
            return result.tags

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(assign, 1, " Python ")
        second = pool.submit(assign, 2, "PYTHON")
        assert first.result(timeout=10) == second.result(timeout=10) == ["python"]
    with Session(postgres_engine) as db:
        assert db.scalars(select(models.Tag.name)).all() == ["python"]
        assert db.execute(select(models.post_tags).order_by(models.post_tags.c.post_id)).all() == [
            (1, "python"), (2, "python"),
        ]
