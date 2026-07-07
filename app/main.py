import os
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import SessionLocal
from app.models import Product
from app.routers import admin, orders, products
from app.services.csv_import import process_csv


def _run_migrations() -> None:
    """Apply any pending Alembic migrations at startup."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup:
    1. Run 'alembic upgrade head' to apply any pending migrations.
    2. Seed from products.csv if the products table is empty.
    """
    if os.getenv("TESTING") != "true":
        _run_migrations()

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
