
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


load_dotenv()

test_engine = create_engine(os.environ["TEST_DATABASE_URL"])

TestSessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=test_engine,
)


@pytest.fixture
def db_session():
    # Create fresh tables for every test
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
