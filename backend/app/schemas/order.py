"""Pydantic schemas for Order."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    """What the client sends to POST /api/orders."""

    product_id: int
    quantity: int = Field(gt=0, description="Must be a positive integer")


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    created_at: datetime
