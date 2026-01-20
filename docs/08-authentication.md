# Authentication System

JWT-based authentication with access and refresh tokens.

---

## Token Flow Diagram

```
    ┌──────────────┐
    │    Client    │
    └──────┬───────┘
           │ 1. POST /login {email, password}
           ▼
    ┌──────────────┐
    │   Server     │
    │  - Validate  │
    │  - Generate  │
    │    tokens    │
    └──────┬───────┘
           │ 2. Response:
           │    - Body: {access_token}
           │    - Cookie: refresh_token (HttpOnly)
           ▼
    ┌──────────────┐
    │    Client    │
    │ - Store AT   │
    │ - Cookie auto│
    └──────┬───────┘
           │ 3. GET /api/v1/todos
           │    Header: Authorization: Bearer {access_token}
           ▼
    ┌──────────────┐
    │   Server     │
    │ - Validate   │
    │   JWT        │
    │ - Return data│
    └──────┬───────┘
           │ 4. Access token expires (30 min)
           ▼
    ┌──────────────┐
    │    Client    │
    │ POST /refresh│
    │ (cookie sent)│
    └──────┬───────┘
           │ 5. New access_token
           ▼
    ┌──────────────┐
    │   Continue   │
    │   using API  │
    └──────────────┘
```

---

## Token Comparison

| Aspect | Access Token | Refresh Token |
|--------|--------------|---------------|
| Lifetime | 30 minutes | 7 days |
| Storage | Client memory / localStorage | HttpOnly cookie |
| Purpose | API authentication | Obtain new access tokens |
| Can be stolen via XSS? | Yes (if in localStorage) | No (HttpOnly) |
| Revocable? | No (stateless) | Yes (database check) |

---

## JWT Payload Structure

```json
{
  "sub": "user@example.com",
  "user_id": 1,
  "role": "user",
  "exp": 1642345678,
  "type": "access"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sub` | string | User's email (standard JWT claim) |
| `user_id` | int | Database primary key |
| `role` | string | User role ("user" or "admin") |
| `exp` | int | Expiration timestamp (Unix) |
| `type` | string | Token type ("access") |

---

## Authentication Flow Code

### 1. Login

```python
# Route: POST /api/v1/users/login
tokens = controller.login_user(form_data, db)

# Set refresh token as HttpOnly cookie
response.set_cookie(
    key="refresh_token",
    value=tokens["refresh_token"],
    max_age=604800,  # 7 days
    httponly=True,
    secure=False,    # True in production
    samesite="lax"
)

# Return access token in body
return {"access_token": tokens["access_token"], "token_type": "bearer"}
```

### 2. Protected Request

```python
# Client sends:
# Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# Middleware validates and adds user to request.state
request.state.user = {
    "sub": "user@example.com",
    "user_id": 1,
    "role": "user"
}
```

### 3. Token Refresh

```python
# Route: POST /api/v1/users/refresh
# Cookie automatically sent with request

refresh_token_value = request.cookies.get("refresh_token")
new_tokens = controller.refresh_access_token(refresh_token_value, db)
return {"access_token": new_tokens["access_token"], "token_type": "bearer"}
```

### 4. Logout

```python
# Route: POST /api/v1/users/logout
refresh_token_value = request.cookies.get("refresh_token")
controller.logout_user(refresh_token_value, db)

# Clear the cookie
response.delete_cookie(key="refresh_token", path="/")
return {"message": "Successfully logged out"}
```

---

## Security Best Practices

1. **Short-lived access tokens** (30 min) limit exposure
2. **HttpOnly cookies** prevent XSS from stealing refresh tokens
3. **Database-backed refresh tokens** allow immediate revocation
4. **Token type in payload** prevents using refresh token as access token
5. **Same-site cookie** protects against CSRF

---

[← Back to Index](./README.md) | [Previous: API Routes](./07-api-routes.md) | [Next: Authorization →](./09-authorization.md)
