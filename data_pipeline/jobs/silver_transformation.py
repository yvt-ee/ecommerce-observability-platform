"""
SILVER layer: clean and validate Bronze orders.

Rules applied, in order:
  1. Cast every column to its proper type (id/product_id -> int,
     unit_price/total_amount -> double, created_at -> timestamp).
  2. Drop exact duplicate order ids (`dropDuplicates`).
  3. Drop rows with a null/blank product name, a null or non-positive
     quantity, a null or non-positive unit price, or an unparsable
     timestamp.
  4. Recompute total_amount as quantity * unit_price -- never trust the
     raw value, since Bronze already showed us it can be wrong.
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType


def read_bronze(spark: SparkSession, bronze_path: str) -> DataFrame:
    return spark.read.format("delta").load(bronze_path)


def clean_orders(bronze_df: DataFrame) -> DataFrame:
    typed_df = bronze_df.select(
        F.col("id").cast(IntegerType()).alias("id"),
        F.col("product_id").cast(IntegerType()).alias("product_id"),
        F.trim(F.col("product_name")).alias("product_name"),
        F.col("quantity").cast(IntegerType()).alias("quantity"),
        F.col("unit_price").cast(DoubleType()).alias("unit_price"),
        F.to_timestamp(F.col("created_at")).alias("created_at"),
    )

    deduped_df = typed_df.dropDuplicates(["id"])

    valid_df = deduped_df.filter(
        F.col("id").isNotNull()
        & F.col("product_id").isNotNull()
        & F.col("product_name").isNotNull()
        & (F.col("product_name") != "")
        & F.col("quantity").isNotNull()
        & (F.col("quantity") > 0)
        & F.col("unit_price").isNotNull()
        & (F.col("unit_price") > 0)
        & F.col("created_at").isNotNull()
    )

    silver_df = valid_df.withColumn(
        "total_amount", F.round(F.col("quantity") * F.col("unit_price"), 2)
    ).withColumn("order_date", F.to_date(F.col("created_at")))

    return silver_df


def write_silver(silver_df: DataFrame, silver_path: str) -> None:
    silver_df.write.format("delta").mode("overwrite").save(silver_path)


def main() -> None:
    import argparse

    from data_pipeline.spark_utils import get_local_spark_session

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronze-path", default="data/delta/bronze/orders")
    parser.add_argument("--silver-path", default="data/delta/silver/orders")
    args = parser.parse_args()

    spark = get_local_spark_session("silver-transformation")
    try:
        bronze_df = read_bronze(spark, args.bronze_path)
        silver_df = clean_orders(bronze_df)
        write_silver(silver_df, args.silver_path)

        raw_count, clean_count = bronze_df.count(), silver_df.count()
        print(
            f"Silver: {clean_count} clean rows written to {args.silver_path} "
            f"({raw_count - clean_count} of {raw_count} raw rows dropped)"
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
