import uuid

import httpx


BASE_URL = "http://127.0.0.1:8000"
email = f"demo_{uuid.uuid4().hex[:8]}@example.com"
password = "secret123"


with httpx.Client(base_url=BASE_URL, timeout=10) as client:

    # Register
    response = client.post(
        "/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Demo User",
        },
    )
    response.raise_for_status()
    print("Registration: OK")

    # Login
    response = client.post(
        "/token",
        data={
            "username": email,
            "password": password,
        },
    )
    response.raise_for_status()

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login: OK")

    # Current user
    response = client.get("/me", headers=headers)
    response.raise_for_status()
    print("Current user:", response.json()["email"])

    # Products
    response = client.get("/products", headers=headers)
    response.raise_for_status()

    products = response.json()
    if not products:
        raise RuntimeError("No products found")

    product_id = products[0]["id"]
    print("Products:", len(products))

    # Create order
    response = client.post(
        "/orders",
        json={"product_id": product_id, "quantity": 2},
        headers=headers,
    )
    response.raise_for_status()

    order = response.json()
    order_id = order["id"]
    print("Created order:", order_id)

    # Get orders
    response = client.get("/orders", headers=headers)
    response.raise_for_status()
    print("Orders:", len(response.json()))

    # Get one order
    response = client.get(
        f"/orders/{order_id}",
        headers=headers,
    )
    response.raise_for_status()
    print("Order details:", response.json())

print("DEMO COMPLETED SUCCESSFULLY")