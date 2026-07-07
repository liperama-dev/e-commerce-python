# Re-export ORM models so callers can do: from app.models import Product
from app.models.product import Product

__all__ = ["Product"]
