from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    is_draft = Column(Boolean, default=False)

    category_rel = relationship("Category")

    @property
    def category(self) -> str:
        """Helper to return the category name for Pydantic serialization."""
        return self.category_rel.name if self.category_rel else "Misc"
