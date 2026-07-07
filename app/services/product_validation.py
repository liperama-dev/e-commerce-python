from typing import List

from fastapi import HTTPException

from app.models.product import Product

# Fields required before a product can leave draft status (matches CSV import rules).
_PUBLISH_REQUIRED_FIELDS = (
    ("name", "Name"),
    ("price", "Price"),
    ("stock", "Stock"),
    ("weight_kg", "Weight (kg)"),
)


def get_publish_blockers(product: Product) -> List[str]:
    """Return human-readable labels for fields blocking publication."""
    blockers: List[str] = []
    for attr, label in _PUBLISH_REQUIRED_FIELDS:
        value = getattr(product, attr, None)
        if attr == "name":
            if value is None or not str(value).strip():
                blockers.append(label)
        elif value is None:
            blockers.append(label)
    return blockers


def assert_publishable(product: Product) -> None:
    """Raise HTTP 400 if the product is missing required publish fields."""
    blockers = get_publish_blockers(product)
    if not blockers:
        return
    field_list = ", ".join(blockers)
    raise HTTPException(
        status_code=400,
        detail=f"Cannot publish: the following fields must be filled in before publishing: {field_list}",
    )
