"""
Tests for the admin endpoints (CSV import, DB flush).
"""
import io

from tests.conftest import ADMIN_HEADERS

VALID_CSV = """name,sku,description,category,price,stock,weight_kg
Widget A,SKU-A,A great widget,Gadgets,9.99,50,0.2
Widget B,SKU-B,Another widget,Gadgets,14.99,30,0.4
"""

INVALID_KEY_CSV = VALID_CSV


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def test_import_requires_auth(client):
    csv_file = io.BytesIO(VALID_CSV.encode())
    response = client.post(
        "/api/products/import",
        files={"file": ("products.csv", csv_file, "text/csv")},
    )
    assert response.status_code == 401


def test_flush_requires_auth(client):
    response = client.post("/api/products/flush")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/products/import
# ---------------------------------------------------------------------------

def test_import_csv_accepted(client):
    csv_file = io.BytesIO(VALID_CSV.encode())
    response = client.post(
        "/api/products/import",
        files={"file": ("products.csv", csv_file, "text/csv")},
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data


def test_import_rejects_non_csv(client):
    txt_file = io.BytesIO(b"not a csv")
    response = client.post(
        "/api/products/import",
        files={"file": ("data.txt", txt_file, "text/plain")},
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 400


def test_import_status_pending_then_completed(client):
    csv_file = io.BytesIO(VALID_CSV.encode())
    submit = client.post(
        "/api/products/import",
        files={"file": ("products.csv", csv_file, "text/csv")},
        headers=ADMIN_HEADERS,
    )
    assert submit.status_code == 202
    job_id = submit.json()["job_id"]

    # Background tasks run synchronously in TestClient context
    status = client.get(f"/api/products/import/{job_id}", headers=ADMIN_HEADERS)
    assert status.status_code == 200
    data = status.json()
    assert data["status"] in ("completed", "pending")


def test_import_status_not_found(client):
    response = client.get("/api/products/import/nonexistent-id", headers=ADMIN_HEADERS)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/products/flush
# ---------------------------------------------------------------------------

def test_flush_clears_products(client):
    # Create a product first
    client.post(
        "/api/products",
        json={
            "name": "Temp",
            "sku": "SKU-TMP",
            "category": "Misc",
            "price": "1.00",
            "stock": 1,
            "weight_kg": 0.1,
            "is_draft": False,
        },
    )
    assert len(client.get("/api/products").json()) == 1

    response = client.post("/api/products/flush", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert client.get("/api/products").json() == []


def test_import_with_empty_name_and_ampersand(client, db_session):
    from app.services.csv_import import process_csv
    from app.models.product import Product
    
    csv_data = """name,sku,description,category,price,stock,weight_kg
,SKU-EMPTY-NAME,No name description,Sports,10.00,10,1.0
Special Name & Co,SKU-AMP,Ampersand test,Home & Office,20.00,5,2.0
"""
    result = process_csv(csv_data, db_session)
    assert result["imported_count"] == 2
    assert result["discarded_count"] == 0
    
    # Check empty name product is created as draft
    p_empty = db_session.query(Product).filter(Product.sku == "SKU-EMPTY-NAME").first()
    assert p_empty is not None
    assert p_empty.name is None
    assert p_empty.is_draft is True
    
    # Check ampersand product is created and not draft
    p_amp = db_session.query(Product).filter(Product.sku == "SKU-AMP").first()
    assert p_amp is not None
    assert p_amp.name == "Special Name & Co"
    assert p_amp.is_draft is False
