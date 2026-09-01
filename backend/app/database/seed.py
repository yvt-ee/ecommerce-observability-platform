"""
Seeds the products table with a fixed starter catalog if it's empty.

Idempotent: safe to call on every app startup.
"""
from sqlalchemy.orm import Session

from app.models.product import Product

SEED_PRODUCTS = [
    {"name": "Laptop", "price": 1200.00},
    {"name": "Headphones", "price": 150.00},
    {"name": "Keyboard", "price": 80.00},
    {"name": "Mouse", "price": 40.00},
    {"name": "Monitor", "price": 300.00},
    {"name": "Webcam", "price": 60.00},
]


def seed_products(db: Session) -> None:
    existing_count = db.query(Product).count()
    if existing_count > 0:
        return

    for item in SEED_PRODUCTS:
        db.add(Product(name=item["name"], price=item["price"]))
    db.commit()
