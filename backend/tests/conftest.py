import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["ENVIRONMENT"] = "test"
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/learnonline_test",
)

from models.base import Base
from database import get_db
import main as app_module

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app_module.app.dependency_overrides[get_db] = override_get_db
    with TestClient(app_module.app) as c:
        yield c
    app_module.app.dependency_overrides.clear()
