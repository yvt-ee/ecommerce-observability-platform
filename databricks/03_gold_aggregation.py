# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Aggregation
# MAGIC
# MAGIC Builds business-ready aggregates on top of `ecommerce.silver_orders`:
# MAGIC
# MAGIC - `ecommerce.gold_daily_sales`   -- order_date, total_revenue, order_count
# MAGIC - `ecommerce.gold_product_sales` -- product_id, product_name, units_sold, total_revenue
# MAGIC
# MAGIC Same logic as `data_pipeline/jobs/gold_aggregation.py`, adapted to read
# MAGIC/write Unity Catalog tables instead of local Delta paths.

# COMMAND ----------

dbutils.widgets.text("catalog_schema", "ecommerce", "Catalog/schema for the Delta tables")
schema_name = dbutils.widgets.get("catalog_schema")

# COMMAND ----------

from pyspark.sql import functions as F

silver_df = spark.table(f"{schema_name}.silver_orders")

# COMMAND ----------

daily_sales_df = (
    silver_df.groupBy(F.col("order_date"))
    .agg(
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.count("id").alias("order_count"),
    )
    .orderBy("order_date")
)

product_sales_df = (
    silver_df.groupBy("product_id", "product_name")
    .agg(
        F.sum("quantity").alias("units_sold"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
    )
    .orderBy(F.col("total_revenue").desc())
)

# COMMAND ----------

daily_sales_df.write.format("delta").mode("overwrite").saveAsTable(f"{schema_name}.gold_daily_sales")
product_sales_df.write.format("delta").mode("overwrite").saveAsTable(f"{schema_name}.gold_product_sales")

print(f"Gold: daily_sales ({daily_sales_df.count()} days) -> {schema_name}.gold_daily_sales")
print(f"Gold: product_sales ({product_sales_df.count()} products) -> {schema_name}.gold_product_sales")
display(daily_sales_df)  # noqa: F821 -- `display` is provided by the Databricks runtime
display(product_sales_df)  # noqa: F821 -- `display` is provided by the Databricks runtime
