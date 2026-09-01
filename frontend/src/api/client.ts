import type { Analytics, Order, Product } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON; fall back to statusText
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export const api = {
  getProducts: () => request<Product[]>("/api/products"),

  getOrders: () => request<Order[]>("/api/orders"),

  createOrder: (productId: number, quantity: number) =>
    request<Order>("/api/orders", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),

  getAnalytics: () => request<Analytics>("/api/analytics"),
};

export { ApiError };
