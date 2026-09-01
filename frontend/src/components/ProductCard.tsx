import type { Product } from "../types";

interface ProductCardProps {
  product: Product;
  onBuy: (product: Product) => void;
  isSubmitting: boolean;
}

const currencyFormatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export function ProductCard({ product, onBuy, isSubmitting }: ProductCardProps) {
  return (
    <div className="product-card">
      <div className="product-name">{product.name}</div>
      <div className="product-price">{currencyFormatter.format(product.price)}</div>
      <button className="btn btn-primary" onClick={() => onBuy(product)} disabled={isSubmitting}>
        {isSubmitting ? "Placing order..." : "Buy"}
      </button>
    </div>
  );
}
