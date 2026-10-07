from contextlib import closing
from decimal import Decimal
from pathlib import Path
import sqlite3
import subprocess

import pytest

from orders_app.infrastructure.database import reset_database
from orders_app.infrastructure.sqlite_order_repository import SQLiteOrderRepository


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "orders.sqlite3"
    reset_database(path)
    return path


@pytest.fixture
def repository(database_path):
    return SQLiteOrderRepository(database_path)


def test_list_orders_reads_the_seeded_orders(repository):
    orders = repository.list_orders()

    assert [(order.id, order.customer_name, order.total, order.status.value)
            for order in orders] == [
        ("ORD-1001", "Alice", Decimal("84.50"), "pending"),
        ("ORD-1002", "Bob", Decimal("120.00"), "processing"),
        ("ORD-1003", "Carol", Decimal("39.90"), "shipped"),
    ]


def test_get_order_reads_the_requested_order(repository):
    order = repository.get_order("ORD-1002")

    assert order is not None
    assert (order.id, order.customer_name, order.total, order.status.value) == (
        "ORD-1002", "Bob", Decimal("120.00"), "processing"
    )


@pytest.mark.parametrize("order_id", ["ORD-9999", "' OR 1=1 --"])
def test_get_order_returns_none_for_an_absent_id(repository, order_id):
    assert repository.get_order(order_id) is None


@pytest.mark.parametrize("cents, expected", [
    (0, "0.00"),
    (1, "0.01"),
    (3990, "39.90"),
    (8450, "84.50"),
    (12000, "120.00"),
    (9007199254740993, "90071992547409.93"),
])
def test_integer_cents_are_reconstructed_exactly(database_path, repository, cents, expected):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "UPDATE orders SET total_cents = ? WHERE id = ?",
                (cents, "ORD-1001"),
            )
        stored = connection.execute(
            "SELECT total_cents, typeof(total_cents) FROM orders WHERE id = ?",
            ("ORD-1001",),
        ).fetchone()

    assert stored == (cents, "integer")
    assert repository.get_order("ORD-1001").total == Decimal(expected)


def test_list_orders_sorts_by_id_regardless_of_insertion_order(database_path, repository):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("DELETE FROM orders")
            connection.executemany(
                "INSERT INTO orders (id, customer_name, total_cents, status) VALUES (?, ?, ?, ?)",
                [
                    ("ORD-1003", "Carol", 3990, "shipped"),
                    ("ORD-1001", "Alice", 8450, "pending"),
                    ("ORD-1002", "Bob", 12000, "processing"),
                ],
            )

    assert [order.id for order in repository.list_orders()] == [
        "ORD-1001", "ORD-1002", "ORD-1003"
    ]


def test_list_orders_returns_an_empty_list(database_path, repository):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("DELETE FROM orders")

    assert repository.list_orders() == []


def test_reading_a_missing_database_does_not_create_it(tmp_path):
    path = tmp_path / "missing.sqlite3"
    repository = SQLiteOrderRepository(path)

    assert not path.exists()
    with pytest.raises(sqlite3.OperationalError):
        repository.list_orders()
    assert not path.exists()


def test_reset_restores_the_same_state_on_consecutive_runs(database_path):
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("DELETE FROM orders WHERE id = 'ORD-1003'")
            connection.execute("UPDATE orders SET total_cents = 1 WHERE id = 'ORD-1001'")
            connection.execute(
                "INSERT INTO orders VALUES ('ORD-9999', 'Demo', 200, 'pending')"
            )

    expected = [
        ("ORD-1001", "Alice", 8450, "pending"),
        ("ORD-1002", "Bob", 12000, "processing"),
        ("ORD-1003", "Carol", 3990, "shipped"),
    ]
    snapshots = []
    for _ in range(2):
        reset_database(database_path)
        with closing(sqlite3.connect(database_path)) as connection:
            snapshots.append(connection.execute(
                "SELECT id, customer_name, total_cents, status FROM orders ORDER BY id"
            ).fetchall())

    assert snapshots == [expected, expected]


def test_make_reset_db_creates_a_database_and_is_repeatable(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    path = tmp_path / "nested directory" / "demo.sqlite3"
    expected = [
        ("ORD-1001", "Alice", 8450, "pending"),
        ("ORD-1002", "Bob", 12000, "processing"),
        ("ORD-1003", "Carol", 3990, "shipped"),
    ]

    for _ in range(2):
        result = subprocess.run(
            ["make", "reset-db", f"DB_PATH={path}"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        with closing(sqlite3.connect(path)) as connection:
            assert connection.execute(
                "SELECT id, customer_name, total_cents, status FROM orders ORDER BY id"
            ).fetchall() == expected
