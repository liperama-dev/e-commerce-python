from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_serializer


class ProductBase(BaseModel):
    name: str
    sku: str
    description: str = ""
    category: str = "Misc"
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: bool = False

    @field_serializer("price")
    def serialize_price(self, price: Optional[Decimal]) -> Optional[float]:
        return float(price) if price is not None else None


class ProductCreate(ProductBase):
    """Schema for creating a new product via the API."""
    pass


class ProductUpdate(BaseModel):
    """Schema for partial updates — all fields are optional."""

    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for serialising a product in API responses."""

    id: int

    model_config = {"from_attributes": True}
