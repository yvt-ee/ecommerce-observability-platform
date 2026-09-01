import { useEffect, useState } from "react";
import { api } from "../api/client";
import { OrderRow } from "../components/OrderRow";
import type { Order } from "../types";

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getOrders()
      .then(setOrders)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load orders"))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <p className="status-text">Loading orders...</p>;
  if (error) return <div className="banner banner-error">{error}</div>;

  return (
    <section>
      <h1>Orders</h1>
      {orders.length === 0 ? (
        <p className="status-text">No orders yet. Buy something from the Products page.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Total</th>
              <th>Placed At</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <OrderRow key={order.id} order={order} />
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
