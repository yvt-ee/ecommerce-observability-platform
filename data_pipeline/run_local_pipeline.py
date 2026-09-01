"""
Runs Bronze -> Silver -> Gold end-to-end on your machine, using
open-source `delta-spark` -- no Databricks workspace required. This is the
fast local-fallback path described in the README; `databricks/` holds the
Databricks-native equivalent of these same jobs.

Usage:
    python data_pipeline/run_local_pipeline.py
"""
from pathlib import Path

from data_pipeline.jobs import bronze_ingestion, gold_aggregation, silver_transformation
from data_pipeline.spark_utils import get_local_spark_session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = str(PROJECT_ROOT / "data" / "orders.csv")
DEFAULT_BRONZE = str(PROJECT_ROOT / "data" / "delta" / "bronze" / "orders")
DEFAULT_SILVER = str(PROJECT_ROOT / "data" / "delta" / "silver" / "orders")
DEFAULT_GOLD_DAILY = str(PROJECT_ROOT / "data" / "delta" / "gold" / "daily_sales")
DEFAULT_GOLD_PRODUCT = str(PROJECT_ROOT / "data" / "delta" / "gold" / "product_sales")


def run(
    source_path: str = DEFAULT_SOURCE,
    bronze_path: str = DEFAULT_BRONZE,
    silver_path: str = DEFAULT_SILVER,
    gold_daily_path: str = DEFAULT_GOLD_DAILY,
    gold_product_path: str = DEFAULT_GOLD_PRODUCT,
) -> None:
    spark = get_local_spark_session("ecommerce-local-pipeline")
    try:
        print("=== BRONZE: raw ingestion ===")
        bronze_df = bronze_ingestion.ingest_to_bronze(spark, source_path, bronze_path)
        print(f"{bronze_df.count()} raw rows -> {bronze_path}\n")

        print("=== SILVER: clean + validate ===")
        # Transforms the in-memory Bronze DataFrame directly (equivalent to
        # re-reading the Bronze Delta table we just wrote, just without the
        # extra I/O round-trip in the local demo path).
        silver_df = silver_transformation.clean_orders(bronze_df)
        silver_transformation.write_silver(silver_df, silver_path)
        raw_count, clean_count = bronze_df.count(), silver_df.count()
        print(f"{clean_count} clean rows -> {silver_path} ({raw_count - clean_count} rows dropped)\n")

        print("=== GOLD: aggregate ===")
        daily_sales_df = gold_aggregation.build_daily_sales(silver_df)
        product_sales_df = gold_aggregation.build_product_sales(silver_df)
        gold_aggregation.write_gold(daily_sales_df, product_sales_df, gold_daily_path, gold_product_path)

        print(f"daily_sales -> {gold_daily_path}")
        daily_sales_df.show(n=daily_sales_df.count(), truncate=False)
        print(f"product_sales -> {gold_product_path}")
        product_sales_df.show(truncate=False)
    finally:
        spark.stop()


if __name__ == "__main__":
    run()
