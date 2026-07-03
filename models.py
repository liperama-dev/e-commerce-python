from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from pydantic import BaseModel
from typing import Optional
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(Text)
    category = Column(String, index=True)
    price = Column(Float, nullable=True)
    stock = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    is_draft = Column(Boolean, default=False)

class ProductBase(BaseModel):
    name: str
    sku: str
    description: str
    category: str
    price: Optional[float] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    weight_kg: Optional[float] = None
    is_draft: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
