"""Business logic for products. Deliberately thin: this is a demo project."""
from sqlalchemy.orm import Session

from app.models.product import Product


def list_products(db: Session) -> list[Product]:
    return db.query(Product).order_by(Product.id).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()
