# Authorization (Middlewares)

Middlewares and role-based access control.

---

## JWT Authentication Middleware

**File**: `middlewares/jwt_middleware.py`

Global middleware that protects all routes except explicitly excluded paths.

```python
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_paths = [
            "/docs", "/openapi.json", "/health",
            "/api/v1/users/login", "/api/v1/users/register",
            "/api/v1/users/verify-otp", "/api/v1/users/refresh", 
            "/api/v1/users/logout"
        ]
        
        # Normalize path (handle trailing slashes)
        request_path = request.url.path.rstrip("/") or "/"
        normalized_excluded = [p.rstrip("/") or "/" for p in excluded_paths]
        
        if request_path in normalized_excluded:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if payload is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
        
        request.state.user = payload  # Store user info for route handlers
        return await call_next(request)
```

### Features

- Path normalization handles trailing slash variations
- Stores decoded JWT payload in `request.state.user`
- Returns JSON errors with proper status codes

### Excluded Paths

| Path | Reason |
|------|--------|
| `/docs` | Swagger UI documentation |
| `/openapi.json` | OpenAPI specification |
| `/health` | Health check endpoint |
| `/api/v1/users/login` | Login doesn't require auth |
| `/api/v1/users/register` | Registration doesn't require auth |
| `/api/v1/users/verify-otp` | OTP verification doesn't require auth |
| `/api/v1/users/refresh` | Uses refresh token cookie |
| `/api/v1/users/logout` | Clearing session |

---

## Role Checker

**File**: `middlewares/role_checker.py`

Dependency for role-based access control on specific routes.

```python
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user_role = user.get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {self.allowed_roles}"
            )
        return True
```

### Usage

```python
from middlewares.role_checker import RoleChecker

# Admin-only endpoint
@router.delete("/", dependencies=[Depends(RoleChecker(["admin"]))])
def admin_only_function():
    pass

# Multiple roles allowed
@router.put("/", dependencies=[Depends(RoleChecker(["admin", "moderator"]))])
def admin_or_moderator_function():
    pass
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 Unauthorized | No user in request.state (not authenticated) |
| 403 Forbidden | User role not in allowed_roles |

---

## User Validation Schema

**File**: `middlewares/auth_validate.py`

Enhanced Pydantic schema with password validation rules.

```python
class UserValidationSchema(BaseModel):
    email: EmailStr                  
    password: str
    
    @field_validator('password')    
    @classmethod
    def validate_password(cls, v):
        if not re.match(r'^[a-zA-Z0-9]{8,30}$', v):
            raise ValueError("Password must be between 8 and 30 characters and contain only alphanumeric characters")
        return v
```

### Password Requirements

| Requirement | Value |
|-------------|-------|
| Minimum length | 8 characters |
| Maximum length | 30 characters |
| Allowed characters | a-z, A-Z, 0-9 (alphanumeric) |

---

## Authorization Flow

```
Request → JWT Middleware → Route Handler → RoleChecker → Business Logic
             ↓                                  ↓
        Validate token                   Check user role
             ↓                                  ↓
        Add to request.state            Allow or deny (403)
```

---

[← Back to Index](./README.md) | [Previous: Authentication](./08-authentication.md) | [Next: OTP Verification →](./10-otp-verification.md)
