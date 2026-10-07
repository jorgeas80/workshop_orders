from typing import Protocol

from .order import Order


class OrderRepository(Protocol):
    """Read orders independently of the storage technology."""

    def list_orders(self) -> list[Order]:
        """Return orders sorted by id, or an empty list if none exist."""
        ...

    def get_order(self, order_id: str) -> Order | None:
        """Return the matching order, or None when it does not exist."""
        ...
