from sqlalchemy.orm import Session

from app.models.category import Category


def get_or_create_category(db: Session, name: str) -> Category:
    """Lookup a category by name, or create it if it doesn't exist."""
    normalized = (name or "").strip() or "Misc"
    category = db.query(Category).filter(Category.name == normalized).first()
    if not category:
        category = Category(name=normalized)
        db.add(category)
        db.flush()  # assign ID without committing the transaction
    return category
