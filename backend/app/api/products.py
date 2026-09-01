"""Product endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import ProductOut
from app.services import product_service
from app.telemetry.otel import get_tracer

router = APIRouter(prefix="/api/products", tags=["products"])
tracer = get_tracer()


@router.get("", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)) -> list[ProductOut]:
    with tracer.start_as_current_span("get_products"):
        return product_service.list_products(db)
