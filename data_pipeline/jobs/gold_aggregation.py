"""
GOLD layer: business-ready aggregates built on top of Silver.

  daily_sales   -- order_date, total_revenue, order_count
  product_sales -- product_id, product_name, units_sold, total_revenue
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def read_silver(spark: SparkSession, silver_path: str) -> DataFrame:
    return spark.read.format("delta").load(silver_path)


def build_daily_sales(silver_df: DataFrame) -> DataFrame:
    return (
        silver_df.groupBy(F.col("order_date"))
        .agg(
            F.round(F.sum("total_amount"), 2).alias("total_revenue"),
            F.count("id").alias("order_count"),
        )
        .orderBy("order_date")
    )


def build_product_sales(silver_df: DataFrame) -> DataFrame:
    return (
        silver_df.groupBy("product_id", "product_name")
        .agg(
            F.sum("quantity").alias("units_sold"),
            F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        )
        .orderBy(F.col("total_revenue").desc())
    )


def write_gold(
    daily_sales_df: DataFrame,
    product_sales_df: DataFrame,
    daily_sales_path: str,
    product_sales_path: str,
) -> None:
    daily_sales_df.write.format("delta").mode("overwrite").save(daily_sales_path)
    product_sales_df.write.format("delta").mode("overwrite").save(product_sales_path)


def main() -> None:
    import argparse

    from data_pipeline.spark_utils import get_local_spark_session

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--silver-path", default="data/delta/silver/orders")
    parser.add_argument("--daily-sales-path", default="data/delta/gold/daily_sales")
    parser.add_argument("--product-sales-path", default="data/delta/gold/product_sales")
    args = parser.parse_args()

    spark = get_local_spark_session("gold-aggregation")
    try:
        silver_df = read_silver(spark, args.silver_path)
        daily_sales_df = build_daily_sales(silver_df)
        product_sales_df = build_product_sales(silver_df)
        write_gold(daily_sales_df, product_sales_df, args.daily_sales_path, args.product_sales_path)

        print(f"Gold: daily_sales ({daily_sales_df.count()} days) -> {args.daily_sales_path}")
        print(f"Gold: product_sales ({product_sales_df.count()} products) -> {args.product_sales_path}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
