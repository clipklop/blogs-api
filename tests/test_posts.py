from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select

from blogs_api import models
from blogs_api.main import app
from blogs_api.oauth2 import create_access_token, get_current_user
from blogs_api.schemas import TokenData

def owner_headers():
    return {"Authorization": f"Bearer {create_access_token({'user_id': 1})}"}


def publish(client, post):
    response = client.put(f"/posts/{post['id']}/publication", json={"state": "published"})
    assert response.status_code == 200, response.text
    return response.json()


def create(client, *, publish_now=False, **changes):
    payload = {"title": "Example post", "content": "Example content", **changes}
    response = client.post("/posts/", json=payload)
    assert response.status_code == 201, response.text
    post = response.json()
    return publish(client, post) if publish_now else post


def test_crud_and_stable_slug(client):
    post = create(client)
    assert post["owner_id"] == 1
    assert post["state"] == "draft"
    assert post["published_at"] is None
    assert "published" not in post
    assert client.get(f"/posts/{post['id']}").json() == {**post, "votes": 0}
    updated = client.patch(f"/posts/{post['id']}", json={"title": "New title"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "New title"
    assert updated.json()["content"] == post["content"]
    assert updated.json()["state"] == "draft"
    assert updated.json()["slug"] == post["slug"]
    deleted = client.delete(f"/posts/{post['id']}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/posts/{post['id']}").status_code == 404


def test_public_slug_lookup_and_unique_slugs(client):
    first = create(client, publish_now=True)
    second = create(client)
    assert first["slug"] != second["slug"]
    app.dependency_overrides.pop(get_current_user)
    response = client.get(f"/posts/slug/{first['slug']}")
    assert response.status_code == 200
    assert response.json()["id"] == first["id"]
    assert client.get("/posts/slug/missing").status_code == 404


def test_non_ascii_title_has_valid_slug(client):
    post = create(client, publish_now=True, title="日本語")
    assert post["slug"].startswith("post-")
    assert client.get(f"/posts/slug/{post['slug']}").status_code == 200


@pytest.mark.parametrize("method,payload", [("get", None), ("patch", {"title": "Updated"}), ("delete", None)])
def test_missing_post(client, method, payload):
    kwargs = {"json": payload} if payload else {}
    assert getattr(client, method)("/posts/999", **kwargs).status_code == 404


@pytest.mark.parametrize("payload", [
    {}, {"title": None}, {"content": None}, {"published": None}, {"state": "draft"}, {"published_at": None}, {"rating": None},
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
        create(client, title="First title", content="Needle in content", publish_now=True),
        create(client, title="NEEDLE title", content="Other text"),
        create(client, title="Third title", content="Other text", publish_now=True),
    ]
    # Equal timestamps exercise the ID tie-breaker in both directions.
    for post in db.scalars(select(models.Post)):
        post.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.commit()
    ids = lambda url: [post["id"] for post in client.get(url, headers=owner_headers()).json()]
    expected = [post["id"] for post in posts]
    assert ids("/posts/") == [expected[2], expected[0]]
    assert ids("/posts/?scope=mine") == expected[::-1]
    assert ids("/posts/?scope=mine&sort=oldest") == expected
    assert ids("/posts/?scope=mine&limit=1&offset=1") == [expected[1]]
    assert ids("/posts/?offset=99") == []
    assert ids("/posts/?state=published&sort=oldest") == [expected[0], expected[2]]
    assert ids("/posts/?scope=mine&state=draft") == [expected[1]]
    assert ids("/posts/?scope=mine&search=needle&sort=oldest") == expected[:2]
    assert ids("/posts/?search=needle&state=published&limit=1") == expected[:1]
    assert ids("/posts/?scope=mine&state=draft&search=needle&sort=oldest&limit=1") == [expected[1]]
    assert ids("/posts/?search=absent") == []


def test_search_treats_wildcards_literally(client):
    matching = create(client, publish_now=True, content="100% complete_with care")
    create(client, publish_now=True, content="Other text")
    for search in ["%25", "_"]:
        response = client.get(f"/posts/?search={search}")
        assert [p["id"] for p in response.json()] == [matching["id"]]


def test_default_limit(client):
    for index in range(21):
        create(client, publish_now=True, title=f"Post {index}")
    assert len(client.get("/posts/").json()) == 20


def test_sort_uses_timestamp_before_id(client, db):
    first = create(client, publish_now=True)
    second = create(client, publish_now=True)
    db.get(models.Post, first["id"]).created_at = datetime(2026, 2, 1, tzinfo=timezone.utc)
    db.get(models.Post, second["id"]).created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.commit()
    assert [p["id"] for p in client.get("/posts/?sort=newest").json()] == [first["id"], second["id"]]
    assert [p["id"] for p in client.get("/posts/?sort=oldest").json()] == [second["id"], first["id"]]


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1", "sort=invalid", "search=", "published=false", "state=draft", "state=archived", "state=invalid", "scope=invalid"])
def test_invalid_list_parameters(client, query):
    assert client.get(f"/posts/?{query}").status_code == 422


def test_vote_counts(client, db):
    post = create(client, publish_now=True)
    db.add(models.Vote(user_id=1, post_id=post["id"]))
    db.commit()
    assert client.get("/posts/").json()[0]["votes"] == 1
    assert client.get(f"/posts/{post['id']}").json()["votes"] == 1
    assert client.get(f"/posts/slug/{post['slug']}").json()["votes"] == 1


def test_only_owner_can_modify(client):
    post = create(client, publish_now=True)
    app.dependency_overrides[get_current_user] = lambda: TokenData(id=2)
    assert client.patch(f"/posts/{post['id']}", json={"title": "Changed"}).status_code == 403
    assert client.delete(f"/posts/{post['id']}").status_code == 403


def test_database_constraints_match_schema(engine):
    inspector = inspect(engine)
    columns = {column["name"]: column for column in inspector.get_columns("posts")}
    for field in ["title", "content", "state", "rating", "slug", "created_at", "updated_at"]:
        assert columns[field]["nullable"] is False
    assert columns["owner_id"]["nullable"] is False
    assert columns["published_at"]["nullable"] is True
    assert "published" not in columns
    assert any(index["unique"] and index["column_names"] == ["slug"] for index in inspector.get_indexes("posts"))


@pytest.mark.parametrize("field", ["state", "published", "published_at"])
def test_create_rejects_publication_fields(client, field):
    response = client.post("/posts/", json={"title": "Example", "content": "Text", field: None})
    assert response.status_code == 422
    assert client.get("/posts/?scope=mine", headers=owner_headers()).json() == []


@pytest.mark.parametrize("start", ["draft", "published", "archived"])
@pytest.mark.parametrize("target", ["draft", "published", "archived"])
def test_publication_transition_table(client, db, start, target):
    post = create(client)
    url = f"/posts/{post['id']}/publication"
    if start != "draft":
        assert client.put(url, json={"state": start}).status_code == 200
    before = db.get(models.Post, post["id"])
    before.updated_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    db.commit()
    old_updated_at = client.get(f"/posts/{post['id']}").json()["updated_at"]
    response = client.put(url, json={"state": target})
    if (start, target) == ("archived", "published"):
        assert response.status_code == 409
        assert response.json() == {"detail": "Restore archived posts to draft before publishing"}
        assert client.get(f"/posts/{post['id']}").json()["state"] == "archived"
        return
    assert response.status_code == 200
    result = response.json()
    assert result["state"] == target
    assert (result["updated_at"] == old_updated_at) == (start == target)
    assert (result["published_at"] is not None) == (start == "published" or target == "published")


@pytest.mark.parametrize("payload", [{}, {"state": None}, {"state": "other"}, {"state": "published", "extra": 1}])
def test_invalid_publication_payload(client, payload):
    post = create(client)
    assert client.put(f"/posts/{post['id']}/publication", json=payload).status_code == 422
    assert client.get(f"/posts/{post['id']}").json()["state"] == "draft"


def test_first_publication_survives_edits_and_republication(client):
    post = create(client, publish_now=True)
    first = post["published_at"]
    assert datetime.fromisoformat(first).utcoffset().total_seconds() == 0
    slug_url = f"/posts/slug/{post['slug']}"
    assert client.get(slug_url).status_code == 200
    path = f"/posts/{post['id']}"
    edited = client.patch(path, json={"title": "Edited post"})
    assert edited.json()["published_at"] == first
    for state in ("draft", "archived", "draft", "published"):
        response = client.put(f"{path}/publication", json={"state": state})
        assert response.status_code == 200
        assert response.json()["published_at"] == first
        assert client.get(slug_url).status_code == (200 if state == "published" else 404)


def test_voting_only_on_published_posts(client):
    post = create(client, publish_now=True)
    payload = {"post_id": post["id"], "user_id": 999, "dir": 1}
    assert client.post("/vote/", json=payload).status_code == 201
    assert client.post("/vote/", json=payload).status_code == 409
    path = f"/posts/{post['id']}"
    for state in ("draft", "archived"):
        assert client.put(f"{path}/publication", json={"state": state}).status_code == 200
        for direction in (0, 1):
            blocked = client.post("/vote/", json={**payload, "dir": direction})
            assert blocked.status_code == 404
            assert blocked.json() == {"detail": f"Post with id {post['id']} doesn't exist"}
        assert client.get(path).json()["votes"] == 1
