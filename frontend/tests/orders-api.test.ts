import { describe, expect, it, vi } from "vitest";
import { fetchOrders } from "../src/api/orders";

const order = { id: "ORD-1001", customer_name: "Alice", total: "84.50", status: "pending" };

function respondWith(payload: unknown, status = 200) {
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(payload), { status }));
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

describe("fetchOrders", () => {
  it("interprets the list response and requests the orders endpoint", async () => {
    const fetch = respondWith([order]);

    expect(await fetchOrders()).toEqual([order]);
    expect(fetch).toHaveBeenCalledWith("/api/orders", { signal: undefined });
  });

  it("accepts an empty list", async () => {
    respondWith([]);
    expect(await fetchOrders()).toEqual([]);
  });

  it("rejects an unsuccessful HTTP response", async () => {
    respondWith([order], 500);
    await expect(fetchOrders()).rejects.toThrow("No se pudieron cargar los pedidos.");
  });

  it("propagates a network failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    await expect(fetchOrders()).rejects.toThrow("offline");
  });

  it.each([
    { orders: [order] },
    [null],
    [{ ...order, id: 1001 }],
    [{ ...order, customer_name: null }],
    [{ ...order, total: 84.5 }],
    [{ ...order, total: "84.501" }],
    [{ ...order, status: "unknown" }],
  ].map((payload) => ({ payload })))("rejects data that does not match the JSON contract: $payload", async ({ payload }) => {
    respondWith(payload);
    await expect(fetchOrders()).rejects.toThrow("La respuesta de pedidos no es válida.");
  });

  it("rejects malformed JSON", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{")));
    await expect(fetchOrders()).rejects.toThrow();
  });
});
