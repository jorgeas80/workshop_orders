import { orderStatuses } from "../orders/types";
import type { Order } from "../orders/types";

function isOrder(value: unknown): value is Order {
  if (typeof value !== "object" || value === null) return false;
  const order = value as Record<string, unknown>;
  return (
    typeof order.id === "string" &&
    typeof order.customer_name === "string" &&
    typeof order.total === "string" && /^\d+\.\d{2}$/.test(order.total) &&
    orderStatuses.some((status) => status === order.status)
  );
}

export async function fetchOrders(signal?: AbortSignal): Promise<Order[]> {
  const response = await fetch("/api/orders", { signal });
  if (!response.ok) throw new Error("No se pudieron cargar los pedidos.");
  const data: unknown = await response.json();
  if (!Array.isArray(data) || !data.every(isOrder)) {
    throw new Error("La respuesta de pedidos no es válida.");
  }
  return data;
}
