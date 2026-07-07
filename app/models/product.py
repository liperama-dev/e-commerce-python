from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from app.database import Base


class Product(Base):
    """Core product table — Phase 1 schema (Float price, plain String category)."""

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
