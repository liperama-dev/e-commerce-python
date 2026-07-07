"""
Tests for the product CRUD endpoints.
"""
import pytest
from tests.conftest import ADMIN_HEADERS

PRODUCT_PAYLOAD = {
    "name": "Wireless Headphones",
    "sku": "SKU-WH-001",
    "description": "Premium noise-cancelling headphones",
    "category": "Electronics",
    "price": "49.99",
    "stock": 25,
    "weight_kg": 0.3,
    "is_draft": False,
}


# ---------------------------------------------------------------------------
# GET /api/products
# ---------------------------------------------------------------------------

def test_list_products_empty(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_list_products_returns_created(client):
    client.post("/api/products", json=PRODUCT_PAYLOAD)
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Wireless Headphones"


def test_list_products_excludes_drafts_by_default(client):
    draft = {**PRODUCT_PAYLOAD, "sku": "SKU-DRAFT", "is_draft": True}
    client.post("/api/products", json=draft)
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_list_products_includes_drafts_when_requested(client):
    draft = {**PRODUCT_PAYLOAD, "sku": "SKU-DRAFT", "is_draft": True}
    client.post("/api/products", json=draft)
    response = client.get("/api/products?include_drafts=true")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_products_search(client):
    client.post("/api/products", json=PRODUCT_PAYLOAD)
    other = {**PRODUCT_PAYLOAD, "sku": "SKU-OTH", "name": "USB-C Cable"}
    client.post("/api/products", json=other)

    response = client.get("/api/products?q=Headphone")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sku"] == "SKU-WH-001"


def test_list_products_pagination(client):
    for i in range(5):
        client.post("/api/products", json={**PRODUCT_PAYLOAD, "sku": f"SKU-P{i}"})
    response = client.get("/api/products?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# GET /api/products/{id}
# ---------------------------------------------------------------------------

def test_get_product_found(client):
    created = client.post("/api/products", json=PRODUCT_PAYLOAD).json()
    response = client.get(f"/api/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-WH-001"


def test_get_product_not_found(client):
    response = client.get("/api/products/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/products
# ---------------------------------------------------------------------------

def test_create_product_success(client):
    response = client.post("/api/products", json=PRODUCT_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-WH-001"
    assert data["category"] == "Electronics"
    assert "id" in data


def test_create_product_duplicate_sku(client):
    client.post("/api/products", json=PRODUCT_PAYLOAD)
    response = client.post("/api/products", json=PRODUCT_PAYLOAD)
    assert response.status_code == 400
    assert "SKU" in response.json()["detail"]


# ---------------------------------------------------------------------------
# PUT /api/products/{id}
# ---------------------------------------------------------------------------

def test_update_product_name(client):
    created = client.post("/api/products", json=PRODUCT_PAYLOAD).json()
    response = client.put(f"/api/products/{created['id']}", json={"name": "Studio Headphones"})
    assert response.status_code == 200
    assert response.json()["name"] == "Studio Headphones"


def test_update_product_category(client):
    created = client.post("/api/products", json=PRODUCT_PAYLOAD).json()
    response = client.put(f"/api/products/{created['id']}", json={"category": "Audio"})
    assert response.status_code == 200
    assert response.json()["category"] == "Audio"


def test_update_product_not_found(client):
    response = client.put("/api/products/9999", json={"name": "Ghost"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/products/{id}
# ---------------------------------------------------------------------------

def test_delete_product_success(client):
    created = client.post("/api/products", json=PRODUCT_PAYLOAD).json()
    response = client.delete(f"/api/products/{created['id']}")
    assert response.status_code == 200
    assert client.get(f"/api/products/{created['id']}").status_code == 404


def test_delete_product_not_found(client):
    response = client.delete("/api/products/9999")
    assert response.status_code == 404
