# Testing Guide

Manual and automated testing documentation.

---

## Manual Testing with cURL

### Complete Registration Flow

```bash
# 1. Initiate Registration (sends OTP to email)
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Response: {"message": "Verification code sent to your email", "pending_registration_id": 1}

# 2. Verify OTP (check your email for the 6-digit code)
curl -X POST http://localhost:8000/api/v1/users/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"pending_registration_id": 1, "otp": "123456"}'

# Response: {"id": 1, "email": "test@example.com"}

# 3. Login (save cookies)
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  -c cookies.txt

# 4. Create todo (use access token from login response)
curl -X POST http://localhost:8000/api/v1/todos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"title": "Test todo"}'

# 5. Refresh token
curl -X POST http://localhost:8000/api/v1/users/refresh \
  -b cookies.txt

# 6. Logout
curl -X POST http://localhost:8000/api/v1/users/logout \
  -b cookies.txt
```

---

## Testing with Swagger UI

1. Start the server: `uvicorn index:app --reload`
2. Open `http://localhost:8000/docs` in browser
3. Use the interactive API documentation to test endpoints

### Authenticating in Swagger

1. Call `/api/v1/users/login` with credentials
2. Copy the `access_token` from response
3. Click "Authorize" button at top
4. Enter: `Bearer YOUR_ACCESS_TOKEN`
5. Click "Authorize"

---

## Automated Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py          # Pytest fixtures
├── test_users.py        # User endpoint tests
└── test_todos.py        # Todo endpoint tests
```

### Sample Test

```python
from fastapi.testclient import TestClient
from index import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "pending_registration_id" in response.json()
```

---

## Testing Checklist

### Authentication Tests

- [ ] Register with valid credentials
- [ ] Register with existing email (should fail)
- [ ] Verify OTP with correct code
- [ ] Verify OTP with expired code (should fail)
- [ ] Verify OTP with wrong code (should fail)
- [ ] Login with valid credentials
- [ ] Login with wrong password (should fail)
- [ ] Access protected route with valid token
- [ ] Access protected route without token (should fail)
- [ ] Refresh token before expiry
- [ ] Refresh token after expiry (should fail)
- [ ] Logout clears refresh token

### Authorization Tests

- [ ] User can create own todos
- [ ] User can read own todos
- [ ] User can update own todos
- [ ] User cannot delete todos (admin only)
- [ ] Admin can delete todos

---

## Testing Environment

### Environment Variables for Testing

Create a `.env.test` file:

```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
EMAIL_ADDRESS=test@example.com
EMAIL_PASSWORD=test-password
```

### Database Reset

```bash
# Reset test database
rm test.db
alembic upgrade head
```

---

[← Back to Index](./README.md) | [Previous: API Reference](./12-api-reference.md) | [Next: Configuration →](./14-configuration.md)
