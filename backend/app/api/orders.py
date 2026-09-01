"""Order endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.order import OrderCreate, OrderOut
from app.services import order_service
from app.telemetry.otel import get_tracer

router = APIRouter(prefix="/api/orders", tags=["orders"])
tracer = get_tracer()


@router.get("", response_model=list[OrderOut])
def get_orders(db: Session = Depends(get_db)) -> list[OrderOut]:
    with tracer.start_as_current_span("get_orders"):
        return order_service.list_orders(db)


@router.post("", response_model=OrderOut, status_code=201)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)) -> OrderOut:
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.product_id", order_in.product_id)
        span.set_attribute("order.quantity", order_in.quantity)
        order = order_service.create_order(db, order_in)
        span.set_attribute("order.total_amount", order.total_amount)
        return order
