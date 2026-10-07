import { useEffect, useState } from "react";
import { fetchOrders } from "../../api/orders";
import type { Order } from "../types";

type OrdersState =
  | { type: "loading" }
  | { type: "success"; orders: Order[] }
  | { type: "error" };

export function useOrders() {
  const [state, setState] = useState<OrdersState>({ type: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState({ type: "loading" });
    fetchOrders(controller.signal).then(
      (orders) => {
        if (!controller.signal.aborted) setState({ type: "success", orders });
      },
      () => {
        if (!controller.signal.aborted) setState({ type: "error" });
      },
    );
    return () => controller.abort();
  }, [attempt]);

  return { state, retry: () => setAttempt((value) => value + 1) };
}
