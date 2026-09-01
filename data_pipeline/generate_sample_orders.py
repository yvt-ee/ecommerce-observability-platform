"""
Generates a realistic sample data/orders.csv for demoing the pipeline
without needing a live FastAPI + SQLite instance running first.

In the real workflow this file is produced by
`backend/scripts/export_orders.py` reading actual orders out of SQLite.
This script exists purely so the PySpark pipeline has something to chew on
out of the box, and it deliberately injects a few bad rows (duplicates,
nulls, a negative quantity, a mismatched total) so the Silver
transformation's cleaning logic has real work to do and is demonstrable.

Usage:
    python data_pipeline/generate_sample_orders.py
"""
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.csv"

PRODUCTS = [
    (1, "Laptop", 1200.00),
    (2, "Headphones", 150.00),
    (3, "Keyboard", 80.00),
    (4, "Mouse", 40.00),
    (5, "Monitor", 300.00),
    (6, "Webcam", 60.00),
]

DAYS_OF_HISTORY = 14
ORDERS_PER_DAY_RANGE = (8, 22)

COLUMNS = ["id", "product_id", "product_name", "quantity", "unit_price", "total_amount", "created_at"]


def generate_rows(seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    order_id = 1
    start_date = datetime.now(timezone.utc) - timedelta(days=DAYS_OF_HISTORY)

    for day_offset in range(DAYS_OF_HISTORY):
        day = start_date + timedelta(days=day_offset)
        num_orders = rng.randint(*ORDERS_PER_DAY_RANGE)

        for _ in range(num_orders):
            product_id, product_name, unit_price = rng.choice(PRODUCTS)
            quantity = rng.randint(1, 4)
            created_at = day + timedelta(
                hours=rng.randint(0, 23), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59)
            )
            rows.append(
                {
                    "id": order_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_amount": round(quantity * unit_price, 2),
                    "created_at": created_at.isoformat(),
                }
            )
            order_id += 1

    # --- Deliberately inject bad data for the Silver layer to clean up ---

    # 1. Exact duplicate row (same id) -> should be de-duplicated.
    rows.append(dict(rows[0]))

    # 2. Null quantity -> should be dropped.
    bad_row_1 = dict(rows[5])
    bad_row_1["id"] = order_id
    bad_row_1["quantity"] = ""
    rows.append(bad_row_1)
    order_id += 1

    # 3. Negative quantity -> should be dropped.
    bad_row_2 = dict(rows[6])
    bad_row_2["id"] = order_id
    bad_row_2["quantity"] = -2
    rows.append(bad_row_2)
    order_id += 1

    # 4. Null/missing product_name -> should be dropped.
    bad_row_3 = dict(rows[7])
    bad_row_3["id"] = order_id
    bad_row_3["product_name"] = ""
    rows.append(bad_row_3)
    order_id += 1

    # 5. total_amount inconsistent with quantity * unit_price -> Silver
    #    recomputes total_amount rather than trusting the raw value.
    bad_row_4 = dict(rows[8])
    bad_row_4["id"] = order_id
    bad_row_4["total_amount"] = 999999.99
    rows.append(bad_row_4)

    return rows


def main() -> None:
    rows = generate_rows()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} sample orders (including intentionally dirty rows) to {OUT_PATH}")


if __name__ == "__main__":
    main()
