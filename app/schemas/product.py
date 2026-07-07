from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    sku: str
    description: str = ""
    category: str = "Misc"
    price: Optional[float] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: bool = False


class ProductCreate(ProductBase):
    """Schema for creating a new product via the API."""
    pass


class ProductUpdate(BaseModel):
    """Schema for partial updates — all fields are optional."""

    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for serialising a product in API responses."""

    id: int

    model_config = {"from_attributes": True}
