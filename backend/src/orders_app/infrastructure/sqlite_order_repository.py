from contextlib import closing
from decimal import Decimal
from pathlib import Path
import sqlite3

from ..domain.order import Order, OrderStatus


def _to_order(row: sqlite3.Row) -> Order:
    return Order(
        id=row["id"],
        customer_name=row["customer_name"],
        total=Decimal(row["total_cents"]) / Decimal(100),
        status=OrderStatus(row["status"]),
    )


class SQLiteOrderRepository:
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path).resolve()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path.as_uri() + "?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def list_orders(self) -> list[Order]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, customer_name, total_cents, status FROM orders ORDER BY id"
            ).fetchall()
            return [_to_order(row) for row in rows]

    def get_order(self, order_id: str) -> Order | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT id, customer_name, total_cents, status FROM orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            return _to_order(row) if row is not None else None
