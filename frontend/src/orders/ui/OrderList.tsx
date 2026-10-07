import type { Order } from "../types";
import { OrderCard } from "./OrderCard";

export function OrderList({ orders }: { orders: Order[] }) {
  return (
    <ul className="order-list" aria-label="Pedidos">
      {orders.map((order) => <li key={order.id}><OrderCard order={order} /></li>)}
    </ul>
  );
}
