import type { Order } from "../types";

const currencyFormatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

interface OrderRowProps {
  order: Order;
}

export function OrderRow({ order }: OrderRowProps) {
  const placedAt = new Date(order.created_at).toLocaleString();

  return (
    <tr>
      <td>#{order.id}</td>
      <td>{order.product_name}</td>
      <td>{order.quantity}</td>
      <td>{currencyFormatter.format(order.unit_price)}</td>
      <td>{currencyFormatter.format(order.total_amount)}</td>
      <td>{placedAt}</td>
    </tr>
  );
}
