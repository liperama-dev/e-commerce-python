from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PurchaseRequest(BaseModel):
    quantity: int = 1


class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
