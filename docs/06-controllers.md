# Controllers

Controllers orchestrate operations between routes and services, handling HTTP-specific concerns.

---

## UserController

**File**: `controllers/user_controller.py`

### Methods Overview

| Method | Parameters | Returns | Raises | Description |
|--------|------------|---------|--------|-------------|
| `initiate_registration` | `email`, `password`, `db` | `RegisterResponse` | 400, 500 | Start OTP registration |
| `verify_otp` | `pending_id`, `otp`, `db` | `UserResponse` | 400, 404 | Complete registration |
| `create_user` | `user`, `db` | `UserResponse` | 400, 500 | Direct user creation |
| `get_user_by_id` | `user_id`, `db` | `User` | 404 | Fetch user |
| `login_user` | `user`, `db` | `Token` | 401 | Authenticate and generate tokens |
| `refresh_access_token` | `refresh_token_str`, `db` | `dict` | 401 | Issue new access token |
| `logout_user` | `refresh_token_str`, `db` | `dict` | None | Revoke refresh token |

### initiate_registration (OTP Flow)

```python
def initiate_registration(self, email: str, password: str, db) -> RegisterResponse:
    # Check if user already exists
    existing_user = User.get_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Check for existing pending registration
    pending = PendingRegistration.get_by_email(db, email)
    otp = PendingRegistration.generate_otp()
    
    if pending:
        # Update existing with new OTP
        pending.update_otp(db, otp)
    else:
        # Create new pending registration
        pending = PendingRegistration(
            email=email,
            hashed_password=hash_password(password),
            otp_hash=PendingRegistration.hash_otp(otp),
            expires_at=PendingRegistration.get_expiry_time()
        )
        pending.save(db)
    
    # Send OTP email
    send_otp_email(email, otp)
    
    return {"message": "Verification code sent", "pending_registration_id": pending.id}
```

### login_user (Authentication Flow)

```python
def login_user(self, user: UserLogin, db) -> Token:
    user_auth = self.userService.authenticate_user(user.email, user.password, db)
    if not user_auth:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create access token (30 min expiry)
    access_token = create_access_token(
        data={"sub": user_auth.email, "user_id": user_auth.id, "role": user_auth.role or "user"},
        expires_delta=timedelta(minutes=30)
    )
    
    # Create refresh token (7 day expiry)
    refresh_token = RefreshToken(
        token=RefreshToken.generate_token(),
        user_id=user_auth.id,
        expires_at=get_refresh_token_expiry()
    )
    refresh_token.save(db)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer"
    }
```

**JWT Payload Contents**:

| Field | Description |
|-------|-------------|
| `sub` | User's email (standard JWT claim) |
| `user_id` | Database primary key |
| `role` | User role for authorization |
| `exp` | Expiration timestamp |
| `type` | Token type identifier ("access") |

### refresh_access_token

```python
def refresh_access_token(self, refresh_token_str: str, db) -> dict:
    token_record = RefreshToken.get_by_token(db, refresh_token_str)
    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Handle timezone-aware and naive datetimes
    expires_at = token_record.expires_at
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < now:
        token_record.revoke(db)
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    user = self.userService.get_user_by_id(token_record.user_id, db)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role or "user"},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## TodoController

**File**: `controllers/todo_controller.py`

Simple pass-through controller that delegates to `TodoService`:

```python
class TodoController:
    def __init__(self):
        self.service = TodoService()

    def create_todo(self, user_id: int, todo_data: TodoCreate, db: Session) -> TodoResponse:
        return self.service.create_todo(user_id, todo_data, db)

    def get_todos(self, user_id: int, db: Session) -> list[TodoResponse]:
        return self.service.get_todos_by_user(user_id, db)

    def get_todo(self, todo_id: int, db: Session) -> TodoResponse:
        return self.service.get_todo_by_id(todo_id, db)

    def update_todo(self, todo_id: int, todo_data: TodoUpdate, db: Session) -> TodoResponse:
        return self.service.update_todo(todo_id, todo_data, db)

    def delete_todo(self, todo_id: int, db: Session) -> None:
        self.service.delete_todo(todo_id, db)
```

---

[← Back to Index](./README.md) | [Previous: Services](./05-services.md) | [Next: API Routes →](./07-api-routes.md)
