"""
Gold aggregation should correctly sum revenue/order counts per day and
per product from a set of Silver rows.
"""
from datetime import date

from data_pipeline.jobs.gold_aggregation import build_daily_sales, build_product_sales

SILVER_ROWS = [
    {
        "id": 1, "product_id": 1, "product_name": "Laptop", "quantity": 1,
        "unit_price": 1200.0, "total_amount": 1200.0,
        "created_at": "2026-01-01T10:00:00", "order_date": date(2026, 1, 1),
    },
    {
        "id": 2, "product_id": 1, "product_name": "Laptop", "quantity": 2,
        "unit_price": 1200.0, "total_amount": 2400.0,
        "created_at": "2026-01-01T11:00:00", "order_date": date(2026, 1, 1),
    },
    {
        "id": 3, "product_id": 2, "product_name": "Headphones", "quantity": 3,
        "unit_price": 150.0, "total_amount": 450.0,
        "created_at": "2026-01-02T09:00:00", "order_date": date(2026, 1, 2),
    },
]


def test_daily_sales_calculates_correct_revenue(spark):
    silver_df = spark.createDataFrame(SILVER_ROWS)

    result = {row["order_date"]: row for row in build_daily_sales(silver_df).collect()}

    assert result[date(2026, 1, 1)]["total_revenue"] == 3600.0
    assert result[date(2026, 1, 1)]["order_count"] == 2
    assert result[date(2026, 1, 2)]["total_revenue"] == 450.0
    assert result[date(2026, 1, 2)]["order_count"] == 1


def test_product_sales_calculates_correct_revenue(spark):
    silver_df = spark.createDataFrame(SILVER_ROWS)

    result = {row["product_id"]: row for row in build_product_sales(silver_df).collect()}

    assert result[1]["units_sold"] == 3
    assert result[1]["total_revenue"] == 3600.0
    assert result[2]["units_sold"] == 3
    assert result[2]["total_revenue"] == 450.0
