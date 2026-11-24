# Clients API

REST API for user authentication, product catalog, and order management.

## Technologies

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- Pytest
- HTTPX

## Features

- User registration and authentication
- Password hashing
- JWT-based authorization
- User profile endpoint
- Product catalog
- Order creation and management
- Role-based access control (member/admin)
- Input validation
- Automated API tests
- API demonstration script

## Project Structure

```text
clients_api/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_orders.py
│   └── test_quality.py
├── .gitignore
├── demo.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/DATABASE_NAME
TEST_DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/clients_test
SECRET_KEY=YOUR_SECRET_KEY
```

Use a separate PostgreSQL database for testing.

Never commit `.env` or expose secret values.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements-dev.txt
```

## Run the API

```powershell
fastapi dev app/main.py
```

API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /register | Register a user |
| POST | /token | Authenticate and obtain JWT |
| GET | /me | Get current user profile |
| GET | /products | List products |
| GET | /products/{product_id} | Get product details |
| POST | /orders | Create an order |
| GET | /orders | List orders |
| GET | /orders/{order_id} | Get order details |
| PATCH | /orders/{order_id} | Update order status |
| DELETE | /orders/{order_id} | Delete an order |

## Authorization

The API uses JWT Bearer tokens.

- Members can view their own orders and cancel them.
- Administrators can access all orders and manage order statuses.
- Only administrators can delete orders.

## API Demo

The project includes `demo.py`, a demonstration script that tests the main API workflow using HTTPX.

Start the API server first:

```powershell
fastapi dev app/main.py
```

Open a separate terminal and run:

```powershell
python demo.py
```

The script demonstrates:

- User registration
- Authentication and JWT token generation
- Access to the current user profile
- Retrieving products
- Creating an order
- Retrieving the user's orders
- Retrieving a specific order

Expected final message:

```text
DEMO COMPLETED SUCCESSFULLY
```

## Run Tests

- The test database must exist before running tests.
- Tables are created automatically before each test and dropped afterward.
- Never use the main application database as TEST_DATABASE_URL.

```powershell
pytest -v
```

Tests use the separate `TEST_DATABASE_URL` database.

## Test Results

47 passed in 19.82s.