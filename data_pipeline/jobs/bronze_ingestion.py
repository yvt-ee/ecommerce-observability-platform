"""
BRONZE layer: ingest raw order data as-is, adding only ingestion metadata.

No cleaning and no type coercion here beyond what CSV parsing requires --
that's Silver's job. Bronze should always be a faithful copy of what
actually arrived, including anything malformed, so it can be replayed if
a downstream bug is ever found.
"""
from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def read_raw_orders(spark: SparkSession, source_path: str) -> DataFrame:
    """Reads the raw orders CSV, keeping every column as a string.

    Reading everything as string (rather than letting Spark infer types)
    means a malformed value -- an empty quantity, a garbled timestamp --
    lands safely in Bronze as a string instead of silently becoming null
    or failing the whole read.
    """
    return spark.read.option("header", True).csv(source_path)


def ingest_to_bronze(
    spark: SparkSession, source_path: str, bronze_path: str, source_file: str | None = None
) -> DataFrame:
    raw_df = read_raw_orders(spark, source_path)

    bronze_df = raw_df.withColumn(
        "_ingested_at", F.lit(datetime.now(timezone.utc).isoformat())
    ).withColumn("_source_file", F.lit(source_file or source_path))

    bronze_df.write.format("delta").mode("overwrite").save(bronze_path)
    return bronze_df


def main() -> None:
    import argparse

    from data_pipeline.spark_utils import get_local_spark_session

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="data/orders.csv")
    parser.add_argument("--bronze-path", default="data/delta/bronze/orders")
    args = parser.parse_args()

    spark = get_local_spark_session("bronze-ingestion")
    try:
        df = ingest_to_bronze(spark, args.source, args.bronze_path)
        print(f"Bronze: wrote {df.count()} raw rows to {args.bronze_path}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
