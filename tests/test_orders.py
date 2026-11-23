from decimal import Decimal

from app.auth import hash_password
from app.models import Product, User


def test_create_order(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]

    response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["product_id"] == product.id
    assert response.json()["quantity"] == 2
    assert response.json()["user_id"] == 1


def test_get_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 2},
        headers=headers,
    )

    response = client.get("/orders", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["quantity"] == 2


def test_user_cannot_access_another_users_order(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    users = [
        ("buyer1@example.com", "Buyer One"),
        ("buyer2@example.com", "Buyer Two"),
    ]

    tokens = []

    for email, full_name in users:
        client.post(
            "/register",
            json={
                "email": email,
                "password": "secret123",
                "full_name": full_name,
            },
        )

        response = client.post(
            "/token",
            data={"username": email, "password": "secret123"},
        )
        tokens.append(response.json()["access_token"])

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers={"Authorization": f"Bearer {tokens[0]}"},
    )

    order_id = order_response.json()["id"]

    response = client.get(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {tokens[1]}"},
    )

    assert response.status_code == 403


def test_user_can_cancel_own_order(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    order_id = order_response.json()["id"]

    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "cancelled"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_user_cannot_set_paid_status(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    order_id = order_response.json()["id"]

    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "paid"},
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_set_paid_status(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("secret123"),
        full_name="Test Admin",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token_response = client.post(
        "/token",
        data={
            "username": "admin@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    order_id = order_response.json()["id"]

    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "paid"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_user_cannot_delete_order(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    order_id = order_response.json()["id"]

    response = client.delete(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_delete_order(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("secret123"),
        full_name="Test Admin",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token_response = client.post(
        "/token",
        data={
            "username": "admin@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_response = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    order_id = order_response.json()["id"]

    response = client.delete(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert response.status_code == 204

    check_response = client.get(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert check_response.status_code == 404


def test_filter_orders_by_status(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )

    second_order = client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 2},
        headers=headers,
    )

    order_id = second_order.json()["id"]

    client.patch(
        f"/orders/{order_id}",
        json={"status": "cancelled"},
        headers=headers,
    )

    response = client.get(
        "/orders?status=cancelled",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "cancelled"
    assert response.json()[0]["id"] == order_id


def test_filter_orders_by_product_id(client, db_session):
    first_product = Product(
        name="Product One",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    second_product = Product(
        name="Product Two",
        category="Test",
        price=Decimal("20.00"),
        stock=10,
    )

    db_session.add_all([first_product, second_product])
    db_session.commit()
    db_session.refresh(first_product)
    db_session.refresh(second_product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/orders",
        json={"product_id": first_product.id, "quantity": 1},
        headers=headers,
    )
    client.post(
        "/orders",
        json={"product_id": second_product.id, "quantity": 1},
        headers=headers,
    )

    response = client.get(
        f"/orders?product_id={first_product.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_id"] == first_product.id


def test_limit_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(3):
        client.post(
            "/orders",
            json={"product_id": product.id, "quantity": 1},
            headers=headers,
        )

    response = client.get("/orders?limit=2", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_skip_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(3):
        client.post(
            "/orders",
            json={"product_id": product.id, "quantity": 1},
            headers=headers,
        )

    response = client.get("/orders?skip=2", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_skip_and_limit_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(4):
        client.post(
            "/orders",
            json={"product_id": product.id, "quantity": 1},
            headers=headers,
        )

    response = client.get("/orders?skip=1&limit=2", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_limit_zero_is_rejected(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/orders?limit=0", headers=headers)

    assert response.status_code == 422


def test_limit_over_100_is_rejected(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/orders?limit=101", headers=headers)

    assert response.status_code == 422


def test_negative_skip_is_rejected(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/orders?skip=-1", headers=headers)

    assert response.status_code == 422


def test_admin_can_see_all_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    buyer_token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    buyer_token = buyer_token_response.json()["access_token"]
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

    client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=buyer_headers,
    )

    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("secret123"),
        full_name="Test Admin",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()

    admin_token_response = client.post(
        "/token",
        data={
            "username": "admin@example.com",
            "password": "secret123",
        },
    )
    admin_token = admin_token_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/orders", headers=admin_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] != admin.id


def test_user_sees_only_own_orders(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    users = [
        ("buyer1@example.com", "Buyer One"),
        ("buyer2@example.com", "Buyer Two"),
    ]

    tokens = []

    for email, full_name in users:
        client.post(
            "/register",
            json={
                "email": email,
                "password": "secret123",
                "full_name": full_name,
            },
        )

        response = client.post(
            "/token",
            data={"username": email, "password": "secret123"},
        )
        tokens.append(response.json()["access_token"])

    for token in tokens:
        client.post(
            "/orders",
            json={"product_id": product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

    response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {tokens[1]}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == 2


def test_create_order_with_nonexistent_product(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/orders",
        json={"product_id": 99999, "quantity": 1},
        headers=headers,
    )

    assert response.status_code == 400


def test_create_order_with_zero_quantity(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]

    response = client.post(
        "/orders",
        json={"product_id": 1, "quantity": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_create_order_with_quantity_over_limit(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]

    response = client.post(
        "/orders",
        json={"product_id": 1, "quantity": 11},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_get_orders_without_token(client):
    response = client.get("/orders")

    assert response.status_code == 401


def test_user_cannot_see_other_users_orders_with_filter(client, db_session):
    product = Product(
        name="Test Product",
        category="Test",
        price=Decimal("10.00"),
        stock=10,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    tokens = []

    for email, name in [
        ("buyer1@example.com", "Buyer One"),
        ("buyer2@example.com", "Buyer Two"),
    ]:
        client.post(
            "/register",
            json={
                "email": email,
                "password": "secret123",
                "full_name": name,
            },
        )

        response = client.post(
            "/token",
            data={"username": email, "password": "secret123"},
        )
        tokens.append(response.json()["access_token"])

    client.post(
        "/orders",
        json={"product_id": product.id, "quantity": 1},
        headers={"Authorization": f"Bearer {tokens[0]}"},
    )

    response = client.get(
        f"/orders?product_id={product.id}",
        headers={"Authorization": f"Bearer {tokens[1]}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_order_without_token(client):
    response = client.get("/orders/1")

    assert response.status_code == 401


def test_get_nonexistent_order(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]

    response = client.get(
        "/orders/99999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_update_order_without_token(client):
    response = client.patch(
        "/orders/1",
        json={"status": "cancelled"},
    )

    assert response.status_code == 401


def test_update_nonexistent_order(client):
    client.post(
        "/register",
        json={
            "email": "buyer@example.com",
            "password": "secret123",
            "full_name": "Test Buyer",
        },
    )

    token_response = client.post(
        "/token",
        data={
            "username": "buyer@example.com",
            "password": "secret123",
        },
    )
    token = token_response.json()["access_token"]

    response = client.patch(
        "/orders/99999",
        json={"status": "cancelled"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_delete_order_without_token(client):
    response = client.delete("/orders/1")

    assert response.status_code == 401
