from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select

from blogs_api import models
from blogs_api.main import app
from blogs_api.oauth2 import get_current_user
from blogs_api.schemas import TokenData

def create(client, **changes):
    payload = {"title": "Example post", "content": "Example content", **changes}
    response = client.post("/posts/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_and_stable_slug(client):
    post = create(client)
    assert post["owner_id"] == 1
    assert post["published"] is False
    assert client.get(f"/posts/{post['id']}").json() == {**post, "votes": 0}
    updated = client.patch(f"/posts/{post['id']}", json={"title": "New title", "published": True})
    assert updated.status_code == 200
    assert updated.json()["title"] == "New title"
    assert updated.json()["content"] == post["content"]
    assert updated.json()["published"] is True
    assert updated.json()["slug"] == post["slug"]
    deleted = client.delete(f"/posts/{post['id']}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/posts/{post['id']}").status_code == 404


def test_public_slug_lookup_and_unique_slugs(client):
    first = create(client)
    second = create(client)
    assert first["slug"] != second["slug"]
    app.dependency_overrides.pop(get_current_user)
    response = client.get(f"/posts/slug/{first['slug']}")
    assert response.status_code == 200
    assert response.json()["id"] == first["id"]
    assert client.get("/posts/slug/missing").status_code == 404


def test_non_ascii_title_has_valid_slug(client):
    post = create(client, title="日本語")
    assert post["slug"].startswith("post-")
    assert client.get(f"/posts/slug/{post['slug']}").status_code == 200


@pytest.mark.parametrize("method,payload", [("get", None), ("patch", {"title": "Updated"}), ("delete", None)])
def test_missing_post(client, method, payload):
    kwargs = {"json": payload} if payload else {}
    assert getattr(client, method)("/posts/999", **kwargs).status_code == 404


@pytest.mark.parametrize("payload", [
    {}, {"title": None}, {"content": None}, {"published": None}, {"rating": None},
    {"title": "x"}, {"title": "x" * 101}, {"content": "x" * 1001},
    {"rating": -1}, {"rating": 6}, {"unknown": True}, {"slug": "replace"},
])
def test_invalid_patch_is_rejected(client, payload):
    post = create(client)
    assert client.patch(f"/posts/{post['id']}", json=payload).status_code == 422
    assert client.get(f"/posts/{post['id']}").json()["title"] == post["title"]


@pytest.mark.parametrize("payload", [
    {}, {"title": "x", "content": "ok"}, {"title": "ok", "content": None},
    {"title": "ok", "content": "text", "rating": 6},
])
def test_invalid_create(client, payload):
    assert client.post("/posts/", json=payload).status_code == 422


def test_empty_list(client):
    assert client.get("/posts/").json() == []


def test_pagination_filtering_search_and_sort(client, db):
    posts = [
        create(client, title="First title", content="Needle in content", published=True),
        create(client, title="NEEDLE title", content="Other text", published=False),
        create(client, title="Third title", content="Other text", published=True),
    ]
    # Equal timestamps exercise the ID tie-breaker in both directions.
    for post in db.scalars(select(models.Post)):
        post.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.commit()
    ids = lambda url: [post["id"] for post in client.get(url).json()]
    expected = [post["id"] for post in posts]
    assert ids("/posts/") == expected[::-1]
    assert ids("/posts/?sort=oldest") == expected
    assert ids("/posts/?limit=1&offset=1") == [expected[1]]
    assert ids("/posts/?offset=99") == []
    assert ids("/posts/?published=true&sort=oldest") == [expected[0], expected[2]]
    assert ids("/posts/?published=false") == [expected[1]]
    assert ids("/posts/?search=needle&sort=oldest") == expected[:2]
    assert ids("/posts/?search=needle&published=true&limit=1") == expected[:1]
    assert ids("/posts/?search=absent") == []


def test_search_treats_wildcards_literally(client):
    matching = create(client, content="100% complete_with care")
    create(client, content="Other text")
    for search in ["%25", "_"]:
        response = client.get(f"/posts/?search={search}")
        assert [p["id"] for p in response.json()] == [matching["id"]]


def test_default_limit(client):
    for index in range(21):
        create(client, title=f"Post {index}")
    assert len(client.get("/posts/").json()) == 20


def test_sort_uses_timestamp_before_id(client, db):
    first = create(client)
    second = create(client)
    db.get(models.Post, first["id"]).created_at = datetime(2026, 2, 1, tzinfo=timezone.utc)
    db.get(models.Post, second["id"]).created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.commit()
    assert [p["id"] for p in client.get("/posts/?sort=newest").json()] == [first["id"], second["id"]]
    assert [p["id"] for p in client.get("/posts/?sort=oldest").json()] == [second["id"], first["id"]]


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1", "sort=invalid", "search=", "published=invalid"])
def test_invalid_list_parameters(client, query):
    assert client.get(f"/posts/?{query}").status_code == 422


def test_vote_counts(client, db):
    post = create(client)
    db.add(models.Vote(user_id=1, post_id=post["id"]))
    db.commit()
    assert client.get("/posts/").json()[0]["votes"] == 1
    assert client.get(f"/posts/{post['id']}").json()["votes"] == 1
    assert client.get(f"/posts/slug/{post['slug']}").json()["votes"] == 1


def test_only_owner_can_modify(client):
    post = create(client)
    app.dependency_overrides[get_current_user] = lambda: TokenData(id=2)
    assert client.patch(f"/posts/{post['id']}", json={"title": "Changed"}).status_code == 403
    assert client.delete(f"/posts/{post['id']}").status_code == 403


def test_database_constraints_match_schema(engine):
    inspector = inspect(engine)
    columns = {column["name"]: column for column in inspector.get_columns("posts")}
    for field in ["title", "content", "published", "rating", "slug", "created_at", "updated_at"]:
        assert columns[field]["nullable"] is False
    assert columns["owner_id"]["nullable"] is True
    assert any(index["unique"] and index["column_names"] == ["slug"] for index in inspector.get_indexes("posts"))
