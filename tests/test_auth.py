from datetime import datetime, timedelta, timezone

import jwt
import pytest

from blogs_api import models
from blogs_api.main import app
from blogs_api.oauth2 import ALGORITHM, SECRET_KEY, get_current_user


@pytest.fixture
def auth_client(client):
    app.dependency_overrides.pop(get_current_user)
    return client


def register(client, suffix="one"):
    payload = {"username": f"user-{suffix}", "email": f"{suffix}@example.com", "password": "secret-password"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 201, response.text
    return payload, response.json()


def login(client, payload):
    response = client.post("/login", data={"username": payload["email"], "password": payload["password"]})
    assert response.status_code == 200, response.text
    assert response.json()["token_type"] == "bearer"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_registration_login_and_me(auth_client, db):
    payload, user = register(auth_client)
    headers = login(auth_client, payload)
    response = auth_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == user
    assert "password" not in response.json()
    assert db.get(models.User, user["id"]).password != payload["password"]
    claims = jwt.decode(headers["Authorization"].split()[1], SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["user_id"] == user["id"]
    assert claims["exp"] > datetime.now(timezone.utc).timestamp()


@pytest.mark.parametrize("field", ["email", "username"])
def test_duplicate_registration_and_session_recovery(auth_client, field):
    payload, _ = register(auth_client)
    duplicate = {**payload, "username": "another-user", "email": "another@example.com"}
    duplicate[field] = payload[field]
    assert auth_client.post("/users/", json=duplicate).status_code == 400
    register(auth_client, "after-error")


@pytest.mark.parametrize("password", ["short", "x" * 72, "\U0001f600" * 19])
def test_invalid_registration_password(auth_client, password):
    response = auth_client.post("/users/", json={
        "username": "valid-user", "email": "valid@example.com", "password": password,
    })
    assert response.status_code == 422


@pytest.mark.parametrize("email,password", [
    ("one@example.com", "wrong-password"), ("unknown@example.com", "secret-password"),
    ("one@example.com", "\U0001f600" * 40),
])
def test_invalid_login(auth_client, email, password):
    register(auth_client)
    response = auth_client.post("/login", data={"username": email, "password": password})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("claims", [
    {"user_id": 1, "exp": 0}, {"user_id": 1}, {"exp": 4102444800},
    {"user_id": "bad", "exp": 4102444800}, {"user_id": [], "exp": 4102444800},
    {"user_id": True, "exp": 4102444800}, {"user_id": 0, "exp": 4102444800},
    {"user_id": 1.5, "exp": 4102444800}, {"user_id": 9999, "exp": 4102444800},
    {"user_id": 1, "exp": None}, {"user_id": 1, "exp": []},
])
def test_invalid_claims_return_401(auth_client, claims):
    token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    response = auth_client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_malformed_and_tampered_tokens(auth_client):
    tokens = ["not-a-jwt", jwt.encode({
        "user_id": 1, "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }, "a-different-signing-key-with-at-least-32-bytes", algorithm=ALGORITHM)]
    for token in tokens:
        response = auth_client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401


def test_deleted_user_token_is_rejected(auth_client, db):
    payload, user = register(auth_client)
    headers = login(auth_client, payload)
    db.delete(db.get(models.User, user["id"]))
    db.commit()
    assert auth_client.get("/users/me", headers=headers).status_code == 401
    assert auth_client.post("/posts/", headers=headers, json={"title": "Post", "content": "Content"}).status_code == 401


def test_real_tokens_enforce_post_ownership(auth_client):
    first, owner = register(auth_client)
    second, other = register(auth_client, "two")
    owner_headers = login(auth_client, first)
    other_headers = login(auth_client, second)
    response = auth_client.post("/posts/", headers=owner_headers, json={
        "title": "Owned post", "content": "Content", "owner_id": other["id"],
    })
    assert response.status_code == 201
    post = response.json()
    assert post["owner_id"] == owner["id"]
    assert post["owner"] == owner
    url = f"/posts/{post['id']}"
    assert auth_client.patch(url, headers=other_headers, json={"title": "Stolen"}).status_code == 403
    assert auth_client.delete(url, headers=other_headers).status_code == 403
    assert auth_client.get(url, headers=owner_headers).json()["title"] == "Owned post"
    assert auth_client.patch(url, headers=owner_headers, json={"title": "Updated"}).status_code == 200
    response = auth_client.delete(url, headers=owner_headers)
    assert response.status_code == 204
    assert response.content == b""


def test_protected_routes_require_authentication(auth_client):
    for method, url, kwargs in [
        ("get", "/users/me", {}), ("get", "/posts/1", {}),
        ("post", "/posts/", {"json": {"title": "Post", "content": "Content"}}),
        ("patch", "/posts/1", {"json": {"title": "Updated"}}),
        ("delete", "/posts/1", {}),
    ]:
        response = getattr(auth_client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_disabled_legacy_account_cannot_login(auth_client, db):
    db.add(models.User(username="legacy", email="legacy@example.com", password="!disabled"))
    db.commit()
    response = auth_client.post("/login", data={"username": "legacy@example.com", "password": "!disabled"})
    assert response.status_code == 401
