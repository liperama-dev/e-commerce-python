from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)  # price snapshot at purchase time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
