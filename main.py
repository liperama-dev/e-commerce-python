from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import csv
import io
import math
import os
import re
import bleach

from database import engine, Base, get_db, SessionLocal
from models import Product, ProductBase, ProductCreate, ProductUpdate, ProductResponse

# Create tables
Base.metadata.create_all(bind=engine)

def is_security_threat(value: str) -> bool:
    if not isinstance(value, str):
        return False
    # Check for HTML/XSS using bleach
    cleaned = bleach.clean(value, tags=[], attributes={}, protocols=[], strip=True)
    if cleaned != value and '<' in value and '>' in value:
        return True
    
    # Basic SQLi check
    sqli_pattern = re.compile(r"(?i)(\b(DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+.*?\s+SET|SELECT\s+.*?\s+FROM|UNION\s+ALL|UNION\s+SELECT)\b|--|;\s*$)")
    if sqli_pattern.search(value):
        return True
    
    return False

def process_csv(decoded_content: str, db: Session):
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    imported_count = 0
    discarded_count = 0
    discard_reasons = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            if all(v is None or str(v).strip() == "" for v in row.values()):
                continue

            clean_row = {k.strip() if k else k: v.strip() if isinstance(v, str) else v for k, v in row.items() if k}
            if not any(clean_row.values()):
                continue
                
            name = clean_row.get('name', '')
            if not name.strip():
                discarded_count += 1
                discard_reasons.append({"row": row_num, "reason": "Name cannot be empty or whitespace"})
                continue
                
            threat_found = False
            for k, v in clean_row.items():
                if isinstance(v, str) and is_security_threat(v):
                    discarded_count += 1
                    discard_reasons.append({"row": row_num, "reason": f"Security threat detected in column '{k}'"})
                    threat_found = True
                    break
            
            if threat_found:
                continue

            is_draft = False
                
            try:
                price = float(clean_row.get('price', '').replace('$', '').replace(',', '') or 0)
                if price < 0:
                    price = None
                    is_draft = True
            except ValueError:
                price = None
                is_draft = True
                
            try:
                stock = int(clean_row.get('stock', 0))
                if stock < 0:
                    stock = None
                    is_draft = True
            except ValueError:
                stock = None
                is_draft = True
                
            try:
                weight_kg_raw = clean_row.get('weight_kg', '').strip()
                if weight_kg_raw == '':
                    weight_kg = None
                    is_draft = True
                else:
                    weight_kg = float(weight_kg_raw)
                    if weight_kg < 0:
                        weight_kg = None
                        is_draft = True
            except ValueError:
                weight_kg = None
                is_draft = True

            db_product = db.query(Product).filter(Product.sku == clean_row['sku']).first()
            
            if db_product:
                db_product.name = clean_row['name']
                db_product.description = clean_row.get('description', '')
                db_product.category = clean_row.get('category', 'Misc')
                db_product.price = price
                db_product.stock = stock
                db_product.weight_kg = weight_kg
                db_product.is_draft = is_draft
            else:
                new_product = Product(
                    name=clean_row['name'],
                    sku=clean_row['sku'],
                    description=clean_row.get('description', ''),
                    category=clean_row.get('category', 'Misc'),
                    price=price,
                    stock=stock,
                    weight_kg=weight_kg,
                    is_draft=is_draft
                )
                db.add(new_product)
            
            db.commit()
            imported_count += 1
                
        except Exception as e:
            db.rollback()
            discarded_count += 1
            discard_reasons.append({"row": row_num, "reason": str(e)})
            
    return {
        "message": "CSV processed",
        "imported_count": imported_count,
        "discarded_count": discarded_count,
        "discard_reasons": discard_reasons
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed data on startup
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0 and os.path.exists("products.csv"):
            with open("products.csv", "r", encoding="utf-8", errors="ignore") as f:
                process_csv(f.read(), db)
    finally:
        db.close()
    yield

app = FastAPI(title="E-Commerce API", lifespan=lifespan)

# API Endpoints
@app.get("/api/products", response_model=List[ProductResponse])
def get_products(q: str = "", include_drafts: bool = False, db: Session = Depends(get_db)):
    query = db.query(Product)
    if not include_drafts:
        query = query.filter(Product.is_draft == False)
    if q:
        query = query.filter(Product.name.contains(q) | Product.description.contains(q) | Product.sku.contains(q))
    return query.all()

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.sku == product.sku).first()
    if db_product:
        raise HTTPException(status_code=400, detail="SKU already registered")
    
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"ok": True}

@app.post("/api/products/{product_id}/publish")
def publish_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.is_draft = False
    db.commit()
    return {"message": "Product published"}

@app.post("/api/products/{product_id}/unpublish")
def unpublish_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.is_draft = True
    db.commit()
    return {"message": "Product unpublished"}

@app.post("/api/products/import")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    # Decode keeping it robust against different encodings
    try:
        decoded_content = content.decode('utf-8')
    except UnicodeDecodeError:
        decoded_content = content.decode('iso-8859-1')
        
    return process_csv(decoded_content, db)

@app.post("/api/products/flush")
def flush_database(db: Session = Depends(get_db)):
    db.query(Product).delete()
    db.commit()
    return {"message": "Database flushed successfully"}

class PurchaseRequest(ProductBase):
    pass # We just need something to trigger it, could be empty

@app.post("/api/products/{product_id}/purchase")
def purchase_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if db_product.stock <= 0:
        raise HTTPException(status_code=400, detail="Product is out of stock")
        
    # Fake purchase logic: just decrement stock
    db_product.stock -= 1
    db.commit()
    return {"message": "Purchase successful", "new_stock": db_product.stock}

# Mount static files at the end to not override api routes
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
