import { useState } from "react";
import { Nav, type Page } from "./components/Nav";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { OrdersPage } from "./pages/OrdersPage";
import { ProductsPage } from "./pages/ProductsPage";

function App() {
  const [page, setPage] = useState<Page>("products");

  return (
    <div className="app">
      <Nav active={page} onNavigate={setPage} />
      <main className="app-content">
        {/* Remounting each page on tab switch keeps state management simple:
            every page just fetches fresh data on mount. Fine for this app's size. */}
        {page === "products" && <ProductsPage />}
        {page === "orders" && <OrdersPage />}
        {page === "analytics" && <AnalyticsPage />}
      </main>
    </div>
  );
}

export default App;
