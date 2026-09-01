import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import { ProductCard } from "../components/ProductCard";
import type { Product } from "../types";

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api
      .getProducts()
      .then(setProducts)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load products"))
      .finally(() => setIsLoading(false));
  }, []);

  const handleBuy = async (product: Product) => {
    setSubmittingId(product.id);
    setMessage(null);
    setError(null);
    try {
      await api.createOrder(product.id, 1);
      setMessage(`Order placed for ${product.name}.`);
    } catch (err) {
      const detail = err instanceof ApiError ? err.message : "Could not place order";
      setError(detail);
    } finally {
      setSubmittingId(null);
    }
  };

  if (isLoading) return <p className="status-text">Loading products...</p>;

  return (
    <section>
      <h1>Products</h1>
      {message && <div className="banner banner-success">{message}</div>}
      {error && <div className="banner banner-error">{error}</div>}
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onBuy={handleBuy}
            isSubmitting={submittingId === product.id}
          />
        ))}
      </div>
    </section>
  );
}
