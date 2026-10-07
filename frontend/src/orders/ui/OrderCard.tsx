import type { Order, OrderStatus } from "../types";

const statusLabels: Record<OrderStatus, string> = {
  pending: "Pendiente",
  processing: "En proceso",
  shipped: "Enviado",
  cancelled: "Cancelado",
};

export function OrderCard({ order }: { order: Order }) {
  const headingId = `order-${order.id}`;
  return (
    <article className="order-card" aria-labelledby={headingId}>
      <header className="order-header">
        <h2 id={headingId}>{order.id}</h2>
        <span className={`status status-${order.status}`}>{statusLabels[order.status]}</span>
      </header>
      <dl>
        <div><dt>Cliente</dt><dd>{order.customer_name}</dd></div>
        <div><dt>Total</dt><dd className="order-total">{order.total.replace(".", ",")} €</dd></div>
      </dl>
    </article>
  );
}
