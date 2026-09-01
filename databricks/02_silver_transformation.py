# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Transformation
# MAGIC
# MAGIC Cleans and validates `ecommerce.bronze_orders` into `ecommerce.silver_orders`:
# MAGIC
# MAGIC 1. Casts every column to its proper type.
# MAGIC 2. Drops exact duplicate order ids.
# MAGIC 3. Drops rows with a null/blank product name, a null or non-positive
# MAGIC    quantity, a null or non-positive unit price, or an unparsable timestamp.
# MAGIC 4. Recomputes `total_amount` as `quantity * unit_price` -- the raw value
# MAGIC    is never trusted, since Bronze can (and, in the sample data, does)
# MAGIC    contain rows where it doesn't match.
# MAGIC
# MAGIC This is the same logic as `data_pipeline/jobs/silver_transformation.py`,
# MAGIC adapted to read/write Unity Catalog tables instead of local Delta paths.

# COMMAND ----------

dbutils.widgets.text("catalog_schema", "ecommerce", "Catalog/schema for the Delta tables")
schema_name = dbutils.widgets.get("catalog_schema")

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

bronze_df = spark.table(f"{schema_name}.bronze_orders")

# COMMAND ----------

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

# COMMAND ----------

silver_df.write.format("delta").mode("overwrite").saveAsTable(f"{schema_name}.silver_orders")

raw_count, clean_count = bronze_df.count(), silver_df.count()
print(
    f"Silver: {clean_count} clean rows written to {schema_name}.silver_orders "
    f"({raw_count - clean_count} of {raw_count} raw rows dropped)"
)
display(silver_df.limit(10))  # noqa: F821 -- `display` is provided by the Databricks runtime
