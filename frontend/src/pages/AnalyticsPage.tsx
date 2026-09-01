import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Analytics } from "../types";

const currencyFormatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getAnalytics()
      .then(setAnalytics)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load analytics"))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <p className="status-text">Loading analytics...</p>;
  if (error) return <div className="banner banner-error">{error}</div>;
  if (!analytics) return null;

  const maxRevenue = Math.max(1, ...analytics.revenue_by_day.map((d) => d.total_revenue));

  return (
    <section>
      <h1>Analytics</h1>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Total Revenue</div>
          <div className="stat-value">{currencyFormatter.format(analytics.total_revenue)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Orders</div>
          <div className="stat-value">{analytics.total_orders}</div>
        </div>
      </div>

      <h2>Revenue by Day</h2>
      {analytics.revenue_by_day.length === 0 ? (
        <p className="status-text">No orders yet.</p>
      ) : (
        <div className="bar-chart">
          {analytics.revenue_by_day.map((day) => (
            <div className="bar-chart-column" key={day.order_date}>
              <div className="bar-chart-value">{currencyFormatter.format(day.total_revenue)}</div>
              <div
                className="bar-chart-bar"
                style={{ height: `${Math.max(4, (day.total_revenue / maxRevenue) * 160)}px` }}
              />
              <div className="bar-chart-label">{day.order_date}</div>
            </div>
          ))}
        </div>
      )}

      <h2>Top Products</h2>
      {analytics.top_products.length === 0 ? (
        <p className="status-text">No orders yet.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Units Sold</th>
              <th>Revenue</th>
            </tr>
          </thead>
          <tbody>
            {analytics.top_products.map((product) => (
              <tr key={product.product_id}>
                <td>{product.product_name}</td>
                <td>{product.units_sold}</td>
                <td>{currencyFormatter.format(product.total_revenue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
