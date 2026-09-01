# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze Ingestion
# MAGIC
# MAGIC Reads the raw `orders.csv` export (produced by
# MAGIC `backend/scripts/export_orders.py` from the FastAPI/SQLite operational
# MAGIC database) and lands it, unmodified, as a managed Delta table:
# MAGIC `ecommerce.bronze_orders`.
# MAGIC
# MAGIC No cleaning or type coercion happens here -- that's Silver's job. Bronze
# MAGIC is a faithful copy of exactly what arrived, malformed values included,
# MAGIC so the pipeline can always be replayed from scratch if a downstream bug
# MAGIC is found.
# MAGIC
# MAGIC See the repo README ("Databricks setup") for how to upload `orders.csv`
# MAGIC to a Unity Catalog Volume before running this notebook.

# COMMAND ----------

dbutils.widgets.text("source_path", "/Volumes/ecommerce/default/landing/orders.csv", "Source CSV path")
dbutils.widgets.text("catalog_schema", "ecommerce", "Catalog/schema for the Delta tables")

source_path = dbutils.widgets.get("source_path")
schema_name = dbutils.widgets.get("catalog_schema")

# COMMAND ----------

from datetime import datetime, timezone

from pyspark.sql import functions as F

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

# COMMAND ----------

# Read every column as a string. Letting Spark infer types here would risk
# silently nulling out a malformed value (e.g. a blank quantity) before
# we've even had a chance to record that it arrived that way.
raw_df = spark.read.option("header", True).csv(source_path)

bronze_df = raw_df.withColumn(
    "_ingested_at", F.lit(datetime.now(timezone.utc).isoformat())
).withColumn("_source_file", F.lit(source_path))

# COMMAND ----------

bronze_df.write.format("delta").mode("overwrite").saveAsTable(f"{schema_name}.bronze_orders")

print(f"Bronze: wrote {bronze_df.count()} raw rows to {schema_name}.bronze_orders")
display(bronze_df.limit(10))  # noqa: F821 -- `display` is provided by the Databricks runtime
