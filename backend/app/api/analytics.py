"""Analytics endpoint for the frontend Analytics page."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analytics import AnalyticsOut
from app.services import analytics_service
from app.telemetry.otel import get_tracer

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
tracer = get_tracer()


@router.get("", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db)) -> AnalyticsOut:
    with tracer.start_as_current_span("get_analytics"):
        return analytics_service.get_analytics(db)
