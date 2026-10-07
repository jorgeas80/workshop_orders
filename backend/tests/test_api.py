from contextlib import closing
import sqlite3

from fastapi.testclient import TestClient
import pytest

from orders_app.infrastructure.database import reset_database
from orders_app.main import create_app


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "orders.sqlite3"
    reset_database(path)
    return path


@pytest.fixture
def client(database_path):
    with TestClient(create_app(database_path)) as client:
        yield client


def test_list_orders_returns_200_and_the_public_json_contract(client):
    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == [
        {"id": "ORD-1001", "customer_name": "Alice", "total": "84.50", "status": "pending"},
        {"id": "ORD-1002", "customer_name": "Bob", "total": "120.00", "status": "processing"},
        {"id": "ORD-1003", "customer_name": "Carol", "total": "39.90", "status": "shipped"},
    ]


def test_get_order_returns_200_and_the_requested_order(client):
    response = client.get("/api/orders/ORD-1002")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ORD-1002", "customer_name": "Bob", "total": "120.00", "status": "processing"
    }


def test_get_order_returns_404_when_the_order_is_missing(client):
    response = client.get("/api/orders/ORD-9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_list_orders_returns_200_and_an_empty_list(client, database_path):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("DELETE FROM orders")

    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.json() == []


def test_api_reads_current_data_from_the_real_sqlite_repository(client, database_path):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "UPDATE orders SET customer_name = ?, total_cents = ? WHERE id = ?",
                ("Demo", 1, "ORD-1001"),
            )

    response = client.get("/api/orders/ORD-1001")

    assert response.status_code == 200
    assert response.json() == {
        "id": "ORD-1001", "customer_name": "Demo", "total": "0.01", "status": "pending"
    }
