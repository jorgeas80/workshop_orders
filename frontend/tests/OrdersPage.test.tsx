import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { OrdersPage } from "../src/orders/ui/OrdersPage";

const orders = [
  { id: "ORD-1001", customer_name: "Alice", total: "84.50", status: "pending" },
  { id: "ORD-1002", customer_name: "Bob", total: "120.00", status: "processing" },
  { id: "ORD-1003", customer_name: "Carol", total: "39.90", status: "shipped" },
];

it("renders each order's id, customer, total and status", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(orders))));
  render(<OrdersPage />);

  const list = await screen.findByRole("list", { name: "Pedidos" });
  expect(within(list).getAllByRole("listitem")).toHaveLength(3);
  const alice = within(list).getByRole("article", { name: "ORD-1001" });
  expect(within(alice).getByText("Alice")).toBeVisible();
  expect(within(alice).getByText("84,50 €")).toBeVisible();
  expect(within(alice).getByText("Pendiente")).toBeVisible();
  const bob = within(list).getByRole("article", { name: "ORD-1002" });
  expect(within(bob).getByText("Bob")).toBeVisible();
  expect(within(bob).getByText("120,00 €")).toBeVisible();
  expect(within(bob).getByText("En proceso")).toBeVisible();
  const carol = within(list).getByRole("article", { name: "ORD-1003" });
  expect(within(carol).getByText("Carol")).toBeVisible();
  expect(within(carol).getByText("39,90 €")).toBeVisible();
  expect(within(carol).getByText("Enviado")).toBeVisible();
});

it("shows a loading state while waiting for the response", () => {
  vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
  render(<OrdersPage />);

  expect(screen.getByRole("status")).toHaveTextContent("Cargando pedidos");
});

it("shows an empty state when there are no orders", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("[]")));
  render(<OrdersPage />);

  expect(await screen.findByText("No hay pedidos.")).toBeVisible();
  expect(screen.queryByRole("list")).not.toBeInTheDocument();
});

it("shows a comprehensible error without exposing technical details", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("internal diagnostics")));
  render(<OrdersPage />);

  expect(await screen.findByRole("alert")).toHaveTextContent("No se pudieron cargar los pedidos.");
  expect(screen.queryByText("internal diagnostics")).not.toBeInTheDocument();
});

it("lets the user retry a failed load", async () => {
  const user = userEvent.setup();
  vi.stubGlobal("fetch", vi.fn()
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValueOnce(new Response(JSON.stringify(orders))));
  render(<OrdersPage />);

  await screen.findByRole("alert");
  await user.click(screen.getByRole("button", { name: "Reintentar" }));

  expect(await screen.findByRole("list", { name: "Pedidos" })).toBeVisible();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
