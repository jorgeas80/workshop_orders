from decimal import Decimal

import pytest

from orders_app.domain.order import Order, OrderStatus


def test_order_preserves_the_data_needed_by_the_listing():
    order = Order("ORD-1001", "Alice", Decimal("84.50"), OrderStatus.PENDING)

    assert order.id == "ORD-1001"
    assert order.customer_name == "Alice"
    assert order.total == Decimal("84.50")
    assert order.status == OrderStatus.PENDING


@pytest.mark.parametrize("status", ["pending", "processing", "shipped", "cancelled"])
def test_order_accepts_each_known_status(status):
    order = Order("ORD-1001", "Alice", Decimal("84.50"), status)

    assert isinstance(order.status, OrderStatus)
    assert order.status.value == status


def test_order_rejects_an_unknown_status():
    with pytest.raises(ValueError):
        Order("ORD-1001", "Alice", Decimal("84.50"), "unknown")


@pytest.mark.parametrize("total", ["-0.01", "NaN", "Infinity", "-Infinity", "84.501"])
def test_order_rejects_an_invalid_euro_amount(total):
    with pytest.raises(ValueError):
        Order("ORD-1001", "Alice", Decimal(total), OrderStatus.PENDING)


@pytest.mark.parametrize("total", ["0.00", "84.50", "120.00", "39.90"])
def test_order_accepts_non_negative_amounts_without_losing_cents(total):
    order = Order("ORD-1001", "Alice", Decimal(total), OrderStatus.PENDING)

    assert order.total == Decimal(total)
