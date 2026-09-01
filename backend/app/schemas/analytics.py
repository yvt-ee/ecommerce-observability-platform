"""Pydantic schemas for the /api/analytics response."""
from pydantic import BaseModel


class DailyRevenue(BaseModel):
    order_date: str  # ISO date, e.g. "2026-08-31"
    total_revenue: float
    order_count: int


class ProductRevenue(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    total_revenue: float


class AnalyticsOut(BaseModel):
    total_revenue: float
    total_orders: int
    revenue_by_day: list[DailyRevenue]
    top_products: list[ProductRevenue]
