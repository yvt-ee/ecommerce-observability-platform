"""
Exports the `orders` table from SQLite to a CSV file that the PySpark
Bronze job reads.

    FastAPI / SQLite -> export_orders.py -> data/orders.csv -> PySpark

This is a deliberate batch hand-off: for a demo-sized dataset a scheduled
export is completely sufficient, and it avoids pulling in a streaming
system (e.g. Kafka) just to move a few hundred rows.

Usage:
    python scripts/export_orders.py
    python scripts/export_orders.py --db ./ecommerce.db --out ../data/orders.csv
"""
import argparse
import csv
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "ecommerce.db"
DEFAULT_OUT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "orders.csv"

COLUMNS = [
    "id",
    "product_id",
    "product_name",
    "quantity",
    "unit_price",
    "total_amount",
    "created_at",
]


def export_orders(db_path: Path, out_path: Path) -> int:
    if not db_path.exists():
        raise FileNotFoundError(
            f"SQLite database not found at {db_path}. Run the API at least once so it's created and seeded."
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"SELECT {', '.join(COLUMNS)} FROM orders ORDER BY id").fetchall()
    finally:
        conn.close()

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([row[col] for col in COLUMNS])

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to the SQLite database file")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_PATH, help="Path to write orders.csv to")
    args = parser.parse_args()

    count = export_orders(args.db, args.out)
    print(f"Exported {count} orders to {args.out}")


if __name__ == "__main__":
    main()
