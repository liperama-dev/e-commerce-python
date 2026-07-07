from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import verify_admin_key
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return db.query(Category).order_by(Category.name).all()


@router.post("", response_model=CategoryResponse, status_code=201, dependencies=[Depends(verify_admin_key)])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category. Requires Admin Key."""
    existing = db.query(Category).filter(Category.name == category.name.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_cat = Category(name=category.name.strip())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(verify_admin_key)])
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """Update a category name. Requires Admin Key."""
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
        
    existing = db.query(Category).filter(Category.name == category.name.strip(), Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Another category already has this name")
        
    db_cat.name = category.name.strip()
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.delete("/{category_id}", dependencies=[Depends(verify_admin_key)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category and set associated products to uncategorized. Requires Admin Key."""
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Uncategorize products belonging to this category
    db.query(Product).filter(Product.category_id == category_id).update({"category_id": None})
    
    db.delete(db_cat)
    db.commit()
    return {"ok": True}
