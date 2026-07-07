from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderResponse, PurchaseRequest

router = APIRouter(prefix="/api/products", tags=["orders"])


@router.post("/{product_id}/purchase", response_model=OrderResponse)
def purchase_product(
    product_id: int, request: PurchaseRequest, db: Session = Depends(get_db)
):
    """
    Purchase a product by reducing its stock and creating an order record.
    Uses with_for_update() to prevent race conditions during concurrent purchases.
    Note: SQLite doesn't actually lock on with_for_update, but this works for Postgres.
    """
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .with_for_update()
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock is None or product.stock < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    product.stock -= request.quantity
    
    order = Order(
        product_id=product.id,
        quantity=request.quantity,
        unit_price=product.price or 0
    )
    db.add(order)
    
    db.commit()
    db.refresh(order)

    return order
