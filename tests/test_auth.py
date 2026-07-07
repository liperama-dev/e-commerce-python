"""
Tests for authentication endpoints (login, credential hint).
"""
from tests.conftest import ADMIN_HEADERS


def test_login_success(client):
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["token"] == "changeme"  # matches ADMIN_SECRET_KEY from pytest.ini


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_wrong_username(client):
    resp = client.post("/api/auth/login", json={"username": "hacker", "password": "admin"})
    assert resp.status_code == 401


def test_hint_available_when_testing(client):
    """GET /api/auth/hint should return credentials when TESTING=true (set by pytest.ini)."""
    resp = client.get("/api/auth/hint")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "admin"
    assert data["password"] == "admin"


def test_admin_routes_require_token(client):
    """Ensure the token returned by /login is accepted by protected admin routes."""
    # Login to get token
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    token = login.json()["token"]

    # Use token as X-Admin-Key
    resp = client.post("/api/products/flush", headers={"X-Admin-Key": token})
    assert resp.status_code == 200
