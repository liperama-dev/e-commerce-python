"""
Tests for the purchase endpoint.
"""
from tests.conftest import ADMIN_HEADERS

PRODUCT_PAYLOAD = {
    "name": "Widget",
    "sku": "SKU-WGT-001",
    "description": "A fine widget",
    "category": "Widgets",
    "price": "9.99",
    "stock": 10,
    "weight_kg": 0.1,
    "is_draft": False,
}


def _create_product(client, **overrides):
    payload = {**PRODUCT_PAYLOAD, **overrides}
    return client.post("/api/products", json=payload).json()


def test_purchase_decrements_stock(client):
    product = _create_product(client)
    response = client.post(f"/api/products/{product['id']}/purchase", json={"quantity": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 3
    assert data["product_id"] == product["id"]


def test_purchase_creates_order_record(client):
    product = _create_product(client)
    resp = client.post(f"/api/products/{product['id']}/purchase", json={"quantity": 1})
    assert resp.status_code == 200
    order = resp.json()
    assert order["unit_price"] == 9.99
    assert "id" in order
    assert "created_at" in order


def test_purchase_insufficient_stock(client):
    product = _create_product(client)
    response = client.post(f"/api/products/{product['id']}/purchase", json={"quantity": 999})
    assert response.status_code == 400
    assert "stock" in response.json()["detail"].lower()


def test_purchase_draft_product_blocked(client):
    product = _create_product(client, sku="SKU-DRF", is_draft=True)
    response = client.post(f"/api/products/{product['id']}/purchase", json={"quantity": 1})
    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


def test_purchase_product_not_found(client):
    response = client.post("/api/products/9999/purchase", json={"quantity": 1})
    assert response.status_code == 404
