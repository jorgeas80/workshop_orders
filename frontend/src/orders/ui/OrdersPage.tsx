import { useOrders } from "../application/useOrders";
import { OrderList } from "./OrderList";

export function OrdersPage() {
  const { state, retry } = useOrders();

  return (
    <main className="orders-page">
      <header className="page-header">
        <p className="eyebrow">Workshop Orders</p>
        <h1>Pedidos</h1>
        <p className="intro">Consulta tus pedidos y su estado actual.</p>
      </header>
      {state.type === "loading" && <p className="feedback" role="status">Cargando pedidos…</p>}
      {state.type === "error" && (
        <div className="feedback">
          <p role="alert">No se pudieron cargar los pedidos.</p>
          <button type="button" onClick={retry}>Reintentar</button>
        </div>
      )}
      {state.type === "success" && (
        state.orders.length === 0
          ? <p className="feedback" role="status">No hay pedidos.</p>
          : <OrderList orders={state.orders} />
      )}
    </main>
  );
}
