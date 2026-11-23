NEW_USER = {"email": "ada@example.com", "password": "secret123", "full_name": "Ada Lovelace"}


def test_register_creates_user(client):
    resp = client.post("/register", json=NEW_USER)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == NEW_USER["email"]
    assert "hashed_password" not in body


def test_register_duplicate_email_is_409(client):
    client.post("/register", json=NEW_USER)
    resp = client.post("/register", json=NEW_USER)
    assert resp.status_code == 409


def test_login_returns_bearer_token(client):
    client.post("/register", json=NEW_USER)
    resp = client.post(
        "/token",
        data={"username": NEW_USER["email"], "password": NEW_USER["password"]},
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"


def test_login_with_wrong_password_is_401(client):
    client.post("/register", json=NEW_USER)
    resp = client.post(
        "/token",
        data={"username": NEW_USER["email"], "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_without_token_is_401(client):
    assert client.get("/me").status_code == 401


def test_me_with_garbage_token_is_401(client):
    resp = client.get("/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
