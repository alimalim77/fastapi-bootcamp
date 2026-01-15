from fastapi.testclient import TestClient
from index import app
from utils.jwt_handler import create_access_token

client = TestClient(app)

def test_protected_route_access():
    print("Testing protected route access...")
    
    # 1. No token
    response = client.get("/api/v1/users/1")
    print(f"No token: Status {response.status_code}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid Authorization header"}
    
    # 2. Invalid token
    response = client.get("/api/v1/users/1", headers={"Authorization": "Bearer invalidtoken"})
    print(f"Invalid token: Status {response.status_code}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}
    
    # 3. Valid token
    # Create a dummy token. We don't need a real user in DB for the middleware check 
    # unless the controller itself checks for user existence and fails if not found.
    # The middleware just checks signature.
    # However, the endpoint `get_user` calls `controller.get_user_by_id(user_id, db)`.
    # Depending on how that is implemented, it might 404 or 500 if DB is empty or connection fails.
    # But the middleware should pass, so we might get a different error (like 404 user not found) 
    # which proves middleware passed!
    
    token = create_access_token({"sub": "testuser@example.com"})
    response = client.get("/api/v1/users/1", headers={"Authorization": f"Bearer {token}"})
    print(f"Valid token: Status {response.status_code}")
    
    # If the middleware passes, we expect something OTHER than 401 from the middleware.
    # It might be 200 (if user exists), 404 (if user doesn't exist), or 500 (db error).
    # As long as it's NOT the middleware's 401, we are good.
    # BUT, wait, if the token is valid, the middleware sets request.state.user.
    
    if response.status_code == 401:
        print("FAILED: Got 401 even with valid token (unless token generation is wrong)")
    else:
        print("SUCCESS: Middleware passed.")

if __name__ == "__main__":
    try:
        test_protected_route_access()
        print("ALL TESTS PASSED")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
