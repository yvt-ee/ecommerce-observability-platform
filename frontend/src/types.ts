export interface Product {
  id: number;
  name: string;
  price: number;
}

export interface Order {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  created_at: string;
}

export interface DailyRevenue {
  order_date: string;
  total_revenue: number;
  order_count: number;
}

export interface ProductRevenue {
  product_id: number;
  product_name: string;
  units_sold: number;
  total_revenue: number;
}

export interface Analytics {
  total_revenue: number;
  total_orders: number;
  revenue_by_day: DailyRevenue[];
  top_products: ProductRevenue[];
}
