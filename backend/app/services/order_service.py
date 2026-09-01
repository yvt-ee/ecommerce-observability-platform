"""Business logic for orders."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.order import OrderCreate
from app.services.product_service import get_product


def list_orders(db: Session) -> list[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).all()


def create_order(db: Session, order_in: OrderCreate) -> Order:
    product = get_product(db, order_in.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {order_in.product_id} not found",
        )

    total_amount = round(product.price * order_in.quantity, 2)

    order = Order(
        product_id=product.id,
        product_name=product.name,
        quantity=order_in.quantity,
        unit_price=product.price,
        total_amount=total_amount,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
