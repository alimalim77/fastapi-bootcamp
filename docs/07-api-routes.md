# API Routes

Route definitions and HTTP handlers.

---

## User Routes

**File**: `api/v1/routes/user_routes.py`

**Prefix**: `/api/v1/users`

### Cookie Configuration

```python
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds
```

### Endpoints Overview

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| POST | `/register` | No | Initiate OTP registration |
| POST | `/verify-otp` | No | Complete registration |
| POST | `/login` | No | Authenticate and get tokens |
| POST | `/refresh` | No (cookie) | Get new access token |
| POST | `/logout` | No (cookie) | Revoke refresh token |
| GET | `/{user_id}` | Yes | Get user details |

### Login Endpoint (Cookie Handling)

```python
@router.post("/login")
def login_for_access_token(response: Response, form_data: UserLogin, db: Session = Depends(get_db)):
    tokens = controller.login_user(form_data, db)
    
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=tokens["refresh_token"],
        max_age=REFRESH_TOKEN_MAX_AGE,
        httponly=True,      # Cannot be accessed by JavaScript
        secure=False,       # Set to True in production (HTTPS only)
        samesite="lax",     # CSRF protection
        path="/"            # Send cookie to all routes
    )
    
    return {
        "access_token": tokens["access_token"],
        "token_type": tokens["token_type"]
    }
```

### Cookie Security Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `httponly` | True | Prevents XSS attacks from reading cookie |
| `secure` | False (dev) | Set True for HTTPS in production |
| `samesite` | "lax" | CSRF protection while allowing navigation |
| `path` | "/" | Cookie sent with all requests |

---

## Todo Routes

**File**: `api/v1/routes/todo_routes.py`

**Prefix**: `/api/v1/todos`

All routes require JWT authentication (enforced by middleware).

### User ID Extraction

```python
def get_current_user_id(request: Request) -> int:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if user_id:
        return user_id
    raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")
```

### Endpoints Overview

| Method | Path | Auth Required | Role | Description |
|--------|------|---------------|------|-------------|
| POST | `/` | Yes | Any | Create todo |
| GET | `/` | Yes | Any | List user's todos |
| GET | `/{todo_id}` | Yes | Any | Get single todo |
| PUT | `/{todo_id}` | Yes | Any | Update todo |
| DELETE | `/{todo_id}` | Yes | Admin | Delete todo |

### Admin-Only Delete

```python
@router.delete("/{todo_id}", status_code=204, dependencies=[Depends(RoleChecker(["admin"]))])
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    controller.delete_todo(todo_id, db)
    return None
```

---

[← Back to Index](./README.md) | [Previous: Controllers](./06-controllers.md) | [Next: Authentication →](./08-authentication.md)
