from sqlalchemy.orm import Session

from app.models.category import Category


def get_or_create_category(db: Session, name: str) -> Category:
    """Lookup a category by name, or create it if it doesn't exist."""
    category = db.query(Category).filter(Category.name == name).first()
    if not category:
        category = Category(name=name)
        db.add(category)
        db.flush()  # assign ID without committing the transaction
    return category
