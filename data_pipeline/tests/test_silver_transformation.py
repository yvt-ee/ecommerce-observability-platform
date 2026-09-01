"""
Silver should remove: duplicate ids, null/negative quantity, blank
product names -- and should never trust the raw total_amount.
"""
from data_pipeline.jobs.silver_transformation import clean_orders

BASE_ROW = {
    "id": "1",
    "product_id": "1",
    "product_name": "Laptop",
    "quantity": "2",
    "unit_price": "1200.0",
    "total_amount": "2400.0",
    "created_at": "2026-01-01T10:00:00",
    "_ingested_at": "2026-01-01T10:05:00",
    "_source_file": "test.csv",
}


def _row(**overrides):
    return {**BASE_ROW, **overrides}


def test_silver_removes_invalid_rows(spark):
    raw_rows = [
        _row(id="1"),
        _row(id="1"),  # exact duplicate id -> should be de-duplicated
        _row(id="2", quantity=None),  # null quantity -> dropped
        _row(id="3", quantity="-1"),  # negative quantity -> dropped
        _row(id="4", product_name=""),  # blank product name -> dropped
        _row(id="5", total_amount="999.0"),  # good row, but total_amount is wrong
    ]
    bronze_df = spark.createDataFrame(raw_rows)

    silver_df = clean_orders(bronze_df)
    surviving_ids = {row["id"] for row in silver_df.collect()}

    assert surviving_ids == {1, 5}


def test_silver_recomputes_total_amount_instead_of_trusting_raw_value(spark):
    bronze_df = spark.createDataFrame([_row(id="10", quantity="2", unit_price="1200.0", total_amount="1.00")])

    silver_df = clean_orders(bronze_df)
    row = silver_df.collect()[0]

    assert row["total_amount"] == 2400.0
