"""
Analytics for the frontend Analytics page.

Design note: this computes aggregates directly from the operational SQLite
`orders` table so the UI always has *something* to show without requiring
the Databricks/PySpark pipeline to have run. It intentionally duplicates
(in a much simpler form) what the Gold layer computes -- see the README
"Design decisions" section for the reasoning and the tradeoff.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.analytics import AnalyticsOut, DailyRevenue, ProductRevenue


def get_analytics(db: Session) -> AnalyticsOut:
    total_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0.0)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()

    daily_rows = (
        db.query(
            func.date(Order.created_at).label("order_date"),
            func.sum(Order.total_amount).label("total_revenue"),
            func.count(Order.id).label("order_count"),
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    revenue_by_day = [
        DailyRevenue(order_date=str(row.order_date), total_revenue=round(row.total_revenue, 2), order_count=row.order_count)
        for row in daily_rows
    ]

    product_rows = (
        db.query(
            Order.product_id,
            Order.product_name,
            func.sum(Order.quantity).label("units_sold"),
            func.sum(Order.total_amount).label("total_revenue"),
        )
        .group_by(Order.product_id, Order.product_name)
        .order_by(func.sum(Order.total_amount).desc())
        .all()
    )
    top_products = [
        ProductRevenue(
            product_id=row.product_id,
            product_name=row.product_name,
            units_sold=row.units_sold,
            total_revenue=round(row.total_revenue, 2),
        )
        for row in product_rows
    ]

    return AnalyticsOut(
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        revenue_by_day=revenue_by_day,
        top_products=top_products,
    )
