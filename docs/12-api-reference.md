# API Reference

Complete API endpoints documentation.

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## User Endpoints

### POST /api/v1/users/register

Initiate user registration with OTP verification.

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response** (200):
```json
{
    "message": "Verification code sent to your email",
    "pending_registration_id": 1
}
```

**Errors**:
- 400: User with this email already exists
- 422: Validation error (invalid email or password format)
- 500: Failed to send verification email

---

### POST /api/v1/users/verify-otp

Verify OTP and complete user registration.

**Request Body**:
```json
{
    "pending_registration_id": 1,
    "otp": "123456"
}
```

**Response** (200):
```json
{
    "id": 1,
    "email": "user@example.com"
}
```

**Errors**:
- 400: Invalid verification code
- 400: Verification code expired. Please register again.
- 404: Registration not found

---

### POST /api/v1/users/login

Authenticate and receive tokens.

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response** (200):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Set-Cookie Header**:
```
refresh_token=abc123...; HttpOnly; Max-Age=604800; Path=/; SameSite=lax
```

**Errors**:
- 401: Incorrect email or password

---

### POST /api/v1/users/refresh

Get new access token using refresh token cookie.

**Request**: No body (cookie sent automatically)

**Response** (200):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Errors**:
- 401: Refresh token not found
- 401: Invalid refresh token
- 401: Refresh token expired

---

### POST /api/v1/users/logout

Revoke refresh token and clear cookie.

**Request**: No body

**Response** (200):
```json
{
    "message": "Successfully logged out"
}
```

---

### GET /api/v1/users/{user_id}

Get user details by ID.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200):
```json
{
    "id": 1,
    "email": "user@example.com"
}
```

**Errors**:
- 401: Missing or invalid Authorization header
- 404: User not found

---

## Todo Endpoints

All todo endpoints require authentication.

**Required Header**:
```
Authorization: Bearer {access_token}
```

---

### POST /api/v1/todos/

Create a new todo.

**Request Body**:
```json
{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
}
```

**Response** (201):
```json
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### GET /api/v1/todos/

Get all todos for authenticated user.

**Response** (200):
```json
[
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "user_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]
```

---

### GET /api/v1/todos/{todo_id}

Get a specific todo.

**Response** (200):
```json
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- 404: Todo not found

---

### PUT /api/v1/todos/{todo_id}

Update a todo.

**Request Body** (partial update supported):
```json
{
    "title": "Buy groceries today",
    "completed": true
}
```

**Response** (200):
```json
{
    "id": 1,
    "title": "Buy groceries today",
    "description": "Milk, eggs, bread",
    "completed": true,
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
}
```

**Errors**:
- 404: Todo not found

---

### DELETE /api/v1/todos/{todo_id}

Delete a todo. **Admin only.**

**Response** (204): No content

**Errors**:
- 403: Access denied (not admin)
- 404: Todo not found

---

## Error Response Format

All errors follow this format:

```json
{
    "detail": "Error message here"
}
```

---

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid auth) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (schema validation) |
| 500 | Internal Server Error |

---

[← Back to Index](./README.md) | [Previous: Utilities](./11-utilities.md) | [Next: Testing →](./13-testing.md)
