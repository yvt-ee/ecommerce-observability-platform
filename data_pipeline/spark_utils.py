"""
Shared Spark session helper -- for LOCAL runs only.

Databricks notebooks never need this: a `spark` session (with Delta
already built in) is provided automatically by the Databricks runtime.
This helper exists so the exact same transformation logic in `jobs/` can
also run on a laptop with open-source `delta-spark`, no cluster required.
"""
from pyspark.sql import SparkSession


def get_local_spark_session(app_name: str = "ecommerce-pipeline") -> SparkSession:
    try:
        from delta import configure_spark_with_delta_pip
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "delta-spark is required to run the pipeline locally. Install with:\n"
            "    pip install -r data_pipeline/requirements.txt"
        ) from exc

    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # Keep local demo runs quiet and small.
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.showConsoleProgress", "false")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
