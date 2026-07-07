from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.services.csv_import import process_csv

# NOTE: Prefix kept as /api/products to preserve frontend compatibility.
# Auth protection and background-task promotion come in Phase 5 and Phase 4.
router = APIRouter(prefix="/api/products", tags=["admin"])


@router.post("/import")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file and upsert products synchronously.

    Phase 4 will move this to a background task returning 202 + job_id.
    Phase 5 will gate this endpoint behind X-Admin-Key authentication.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_content = content.decode("iso-8859-1")

    return process_csv(decoded_content, db)


@router.post("/flush")
def flush_database(db: Session = Depends(get_db)):
    """
    Delete all products from the database.

    Phase 5 will gate this endpoint behind X-Admin-Key authentication.
    """
    db.query(Product).delete()
    db.commit()
    return {"message": "Database flushed successfully"}
