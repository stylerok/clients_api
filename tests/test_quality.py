
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from jose import jwt

from app.auth import ALGORITHM, SECRET_KEY, create_access_token
from app.models import Order, Product


def create_product(db_session):
    product = Product(
        name="Quality Test Product",
        category="Test",
        price=Decimal("15.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def create_user_and_headers(client, email="quality@example.com"):
    client.post(
        "/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Quality Test User",
        },
    )

    response = client.post(
        "/token",
        data={
            "username": email,
            "password": "secret123",
        },
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_rejects_invalid_email(client):
    response = client.post(
        "/register",
        json={
            "email": "not-an-email",
            "password": "secret123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = client.post(
        "/register",
        json={
            "email": "short@example.com",
            "password": "123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 422


def test_register_email_is_case_insensitive(client):
    first = client.post(
        "/register",
        json={
            "email": "Ada@example.com",
            "password": "secret123",
            "full_name": "Ada",
        },
    )

    second = client.post(
        "/register",
        json={
            "email": "ADA@example.com",
            "password": "secret123",
            "full_name": "Another Ada",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/token",
        data={
            "username": "unknown@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 401


def test_expired_token_is_rejected(client):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_token_without_subject_is_rejected(client):
    token = create_access_token({})

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_with_non_numeric_subject_is_rejected(client):
    token = create_access_token({"sub": "not-a-number"})

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_for_nonexistent_user_is_rejected(client):
    token = create_access_token({"sub": "999999"})

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_products_requires_authentication(client):
    response = client.get("/products")

    assert response.status_code == 401


def test_get_products(client, db_session):
    product = create_product(db_session)
    headers = create_user_and_headers(client)

    response = client.get("/products", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == product.id


def test_get_nonexistent_product(client, db_session):
    headers = create_user_and_headers(client)

    response = client.get(
        "/products/999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_update_order_rejects_unknown_status(client, db_session):
    product = create_product(db_session)
    headers = create_user_and_headers(client)

    order_response = client.post(
        "/orders",
        json={
            "product_id": product.id,
            "quantity": 1,
        },
        headers=headers,
    )

    assert order_response.status_code == 201

    order_id = order_response.json()["id"]

    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "unknown"},
        headers=headers,
    )

    assert response.status_code == 422


def test_failed_order_does_not_create_database_record(client, db_session):
    headers = create_user_and_headers(client)

    response = client.post(
        "/orders",
        json={
            "product_id": 999999,
            "quantity": 1,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert db_session.query(Order).count() == 0
