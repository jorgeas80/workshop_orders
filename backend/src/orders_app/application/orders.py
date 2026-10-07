from ..domain.order import Order
from ..domain.order_repository import OrderRepository


class OrderNotFound(Exception):
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")


def list_orders(repository: OrderRepository) -> list[Order]:
    return repository.list_orders()


def get_order(repository: OrderRepository, order_id: str) -> Order:
    order = repository.get_order(order_id)
    if order is None:
        raise OrderNotFound(order_id)
    return order
