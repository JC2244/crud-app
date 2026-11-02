# Run using: pytest -v

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base
from main import app, get_db

# Use a temporary in-memory database, so the tests never touch test.db
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Give every test its own empty tables
@pytest.fixture(autouse=True)
def fresh_tables():
    Base.metadata.create_all(bind=engine, tables=[models.Item.__table__])
    yield
    Base.metadata.drop_all(bind=engine)


def create_item(name="pen", description="blue"):
    return client.post("/items/", json={"name": name, "description": description})


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Use the RESTful API"}


def test_create_item():
    response = create_item()
    assert response.status_code == 200
    assert response.json()["name"] == "pen"
    assert response.json()["description"] == "blue"
    assert "id" in response.json()


def test_read_items():
    create_item("pen")
    create_item("book")
    response = client.get("/items/")
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["pen", "book"]


def test_read_one_item():
    item_id = create_item().json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "pen"


def test_read_missing_item_returns_404():
    assert client.get("/items/999").status_code == 404


def test_update_item():
    item_id = create_item().json()["id"]
    response = client.put(
        f"/items/{item_id}", json={"name": "pen", "description": "red"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "red"
    assert client.get(f"/items/{item_id}").json()["description"] == "red"


def test_update_missing_item_returns_404():
    response = client.put("/items/999", json={"name": "x", "description": "y"})
    assert response.status_code == 404


def test_delete_item():
    item_id = create_item().json()["id"]
    assert client.delete(f"/items/{item_id}").status_code == 200
    assert client.get(f"/items/{item_id}").status_code == 404


def test_delete_missing_item_returns_404():
    assert client.delete("/items/999").status_code == 404
