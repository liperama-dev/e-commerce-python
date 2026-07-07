import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.models import Product
from app.routers import admin, orders, products
from app.services.csv_import import process_csv


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup:
    1. Create DB tables (Phase 2 will replace this with 'alembic upgrade head').
    2. Seed from products.csv if the table is empty.
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Product).count() == 0 and os.path.exists("products.csv"):
            with open("products.csv", "r", encoding="utf-8", errors="ignore") as f:
                process_csv(f.read(), db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="E-Commerce API",
    description="Enterprise-grade product catalogue and checkout API.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")
