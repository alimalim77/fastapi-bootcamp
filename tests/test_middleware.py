from utils.jwt_handler import create_access_token
import pytest

def test_protected_route_access_no_token(client):
    """Test that accessing a protected route without a token returns 401."""
    response = client.get("/api/v1/users/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid Authorization header"}

def test_protected_route_access_invalid_token(client):
    """Test that accessing a protected route with an invalid token returns 401."""
    response = client.get("/api/v1/users/1", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}

def test_protected_route_access_valid_token(client):
    """
    Test that accessing a protected route with a valid token does NOT return 401 from middleware.
    Note: It might fail later in the controller (e.g. 404 if DB is empty), but middleware should pass.
    """
    token = create_access_token({"sub": "testuser@example.com"})
    response = client.get("/api/v1/users/1", headers={"Authorization": f"Bearer {token}"})
    
    # Check that we passed the middleware check
    assert response.status_code != 401 or response.json().get("detail") not in [
        "Missing or invalid Authorization header", 
        "Invalid or expired token"
    ]
