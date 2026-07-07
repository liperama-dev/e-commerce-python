from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product

router = APIRouter(prefix="/api/products", tags=["orders"])


@router.post("/{product_id}/purchase")
def purchase_product(product_id: int, db: Session = Depends(get_db)):
    """
    Decrement product stock by 1 and record the purchase.

    Phase 4 will add:
      - row-level locking via .with_for_update()
      - an Order audit record
      - draft-product guard
      - null-stock guard (currently stock=None raises TypeError here)
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if db_product.stock <= 0:
        raise HTTPException(status_code=400, detail="Product is out of stock")

    db_product.stock -= 1
    db.commit()
    return {"message": "Purchase successful", "new_stock": db_product.stock}
