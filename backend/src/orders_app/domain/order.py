from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Order:
    id: str
    customer_name: str
    total: Decimal
    status: OrderStatus

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrderStatus(self.status))
        if not self.total.is_finite() or self.total < 0:
            raise ValueError("Order total must be finite and non-negative")
        if self.total != self.total.quantize(Decimal("0.01")):
            raise ValueError("Order total must be representable in euro cents")
