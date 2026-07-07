from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_serializer


class PurchaseRequest(BaseModel):
    quantity: int = 1


class OrderResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: int
    unit_price: Decimal
    created_at: datetime

    @field_serializer("unit_price")
    def serialize_unit_price(self, v: Optional[Decimal]) -> Optional[float]:
        return float(v) if v is not None else None

    model_config = {"from_attributes": True}
