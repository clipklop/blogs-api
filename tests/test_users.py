from blogs_api import models, utils

def test_read_db_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def create(client, **changes):
    user_data = {
        "username": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        **changes,
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    return response.json()

def test_create_user(client, db):
    user = create(client)

    assert user["username"] == "Test User"
    assert user["email"] == "test@example.com"
    assert "password" not in user
    stored_user = db.get(models.User, user["id"])
    assert stored_user.password != "testpassword"
    assert utils.verify_password("testpassword", stored_user.password)

    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json() == user


def test_create_user_requires_email(client):

    response = client.post("/users/", json={"username": "Another User", "password": "anotherpassword"})
    assert response.status_code == 422  # Expecting validation error due to missing email
