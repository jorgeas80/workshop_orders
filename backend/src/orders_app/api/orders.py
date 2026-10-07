from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..application.orders import OrderNotFound, get_order, list_orders
from ..domain.order import Order, OrderStatus
from ..domain.order_repository import OrderRepository


class OrderResponse(BaseModel):
    id: str
    customer_name: str
    total: str
    status: OrderStatus


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        total=format(order.total, ".2f"),
        status=order.status,
    )


def create_orders_router(repository: OrderRepository) -> APIRouter:
    router = APIRouter(prefix="/api/orders", tags=["orders"])

    @router.get("")
    def list_orders_endpoint() -> list[OrderResponse]:
        return [_to_response(order) for order in list_orders(repository)]

    @router.get("/{order_id}")
    def get_order_endpoint(order_id: str) -> OrderResponse:
        try:
            order = get_order(repository, order_id)
        except OrderNotFound as error:
            raise HTTPException(status_code=404, detail="Order not found") from error
        return _to_response(order)

    return router
