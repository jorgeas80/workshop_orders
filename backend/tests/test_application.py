from decimal import Decimal

import pytest

from orders_app.application.orders import OrderNotFound, get_order, list_orders
from orders_app.domain.order import Order, OrderStatus


class InMemoryOrderRepository:
    def __init__(self, orders: list[Order]) -> None:
        self._orders = {order.id: order for order in orders}

    def list_orders(self) -> list[Order]:
        return sorted(self._orders.values(), key=lambda order: order.id)

    def get_order(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)


@pytest.fixture
def repository() -> InMemoryOrderRepository:
    return InMemoryOrderRepository([
        Order("ORD-1002", "Bob", Decimal("120.00"), OrderStatus.PROCESSING),
        Order("ORD-1001", "Alice", Decimal("84.50"), OrderStatus.PENDING),
    ])


def test_list_orders_returns_the_repository_orders(repository):
    orders = list_orders(repository)

    assert [
        (order.id, order.customer_name, order.total, order.status)
        for order in orders
    ] == [
        ("ORD-1001", "Alice", Decimal("84.50"), OrderStatus.PENDING),
        ("ORD-1002", "Bob", Decimal("120.00"), OrderStatus.PROCESSING),
    ]


def test_list_orders_returns_an_empty_list_when_there_are_no_orders():
    assert list_orders(InMemoryOrderRepository([])) == []


def test_get_order_returns_the_requested_order(repository):
    order = get_order(repository, "ORD-1002")

    assert order.id == "ORD-1002"
    assert order.customer_name == "Bob"
    assert order.total == Decimal("120.00")
    assert order.status == OrderStatus.PROCESSING


def test_get_order_reports_a_missing_order(repository):
    with pytest.raises(OrderNotFound) as error:
        get_order(repository, "ORD-9999")

    assert error.value.order_id == "ORD-9999"
