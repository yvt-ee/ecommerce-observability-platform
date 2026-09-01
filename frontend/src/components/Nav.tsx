export type Page = "products" | "orders" | "analytics";

const TABS: { id: Page; label: string }[] = [
  { id: "products", label: "Products" },
  { id: "orders", label: "Orders" },
  { id: "analytics", label: "Analytics" },
];

interface NavProps {
  active: Page;
  onNavigate: (page: Page) => void;
}

export function Nav({ active, onNavigate }: NavProps) {
  return (
    <header className="nav">
      <div className="nav-brand">Ecommerce Data Platform</div>
      <nav className="nav-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={tab.id === active ? "nav-tab nav-tab-active" : "nav-tab"}
            onClick={() => onNavigate(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
