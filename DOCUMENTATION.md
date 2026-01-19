# FastAPI Bootcamp - Complete Project Documentation

A comprehensive REST API built with FastAPI following clean architecture principles. This documentation covers all modules, functions, database models, authentication flows, and implementation details.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Database Layer](#3-database-layer)
4. [Models](#4-models)
5. [Schemas (Pydantic Models)](#5-schemas-pydantic-models)
6. [Services (Business Logic)](#6-services-business-logic)
7. [Controllers](#7-controllers)
8. [API Routes](#8-api-routes)
9. [Middlewares](#9-middlewares)
10. [Utilities](#10-utilities)
11. [Authentication System](#11-authentication-system)
12. [API Endpoints Reference](#12-api-endpoints-reference)
13. [Testing Guide](#13-testing-guide)
14. [Configuration](#14-configuration)

---

## 1. Project Overview

This project is a FastAPI-based REST API implementing a **Todo application** with full user authentication. It demonstrates best practices in API development including:

- **Clean Architecture**: Separation of concerns with distinct layers (routes, controllers, services, models)
- **JWT Authentication**: Secure access and refresh token system
- **Role-Based Access Control**: Admin-only operations protected by middleware
- **Database Migrations**: Alembic for schema versioning
- **Password Security**: Argon2 hashing algorithm
- **Docker Support**: Containerized deployment

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | SQLite (Development) / PostgreSQL (Production) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT (python-jose) |
| Password Hashing | Argon2 (passlib) |
| Validation | Pydantic |
| Container | Docker |

### Project Structure

```
fastapi-bootcamp/
├── index.py                 # Application entry point
├── api/
│   └── v1/
│       └── routes/
│           ├── user_routes.py    # User API endpoints
│           └── todo_routes.py    # Todo API endpoints
├── controllers/
│   ├── user_controller.py   # User business logic orchestration
│   └── todo_controller.py   # Todo business logic orchestration
├── services/
│   ├── user_service.py      # User domain logic
│   └── todo_service.py      # Todo domain logic
├── models/
│   ├── __init__.py          # Model exports
│   ├── user_model.py        # User SQLAlchemy model
│   ├── todo.py              # Todo SQLAlchemy model
│   └── refresh_token.py     # RefreshToken SQLAlchemy model
├── schemas/
│   ├── user_schema.py       # User Pydantic schemas
│   └── todo_schema.py       # Todo Pydantic schemas
├── middlewares/
│   ├── jwt_middleware.py    # JWT authentication middleware
│   ├── auth_validate.py     # Request validation schemas
│   └── role_checker.py      # Role-based access control
├── utils/
│   ├── jwt_handler.py       # JWT creation and verification
│   ├── hash_generator.py    # Password hashing utilities
│   └── exceptions.py        # Custom exception classes
├── db/
│   ├── database.py          # Database engine configuration
│   └── session.py           # Database session management
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
└── requirements.txt         # Python dependencies
```

---

## 2. Architecture Overview

The application follows a **layered architecture** pattern with clear separation of responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Routes)                      │
│         Handles HTTP requests, response formatting           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Controller Layer                           │
│    Orchestrates business operations, handles HTTP errors     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Service Layer                             │
│        Contains core business logic, domain rules            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Model Layer                              │
│         SQLAlchemy models, database interactions             │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Database                                │
│                SQLite / PostgreSQL                           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Example: User Login

1. **Route** (`user_routes.py`): Receives POST `/api/v1/users/login`
2. **Controller** (`user_controller.py`): Validates, calls service, generates tokens
3. **Service** (`user_service.py`): Authenticates user against database
4. **Model** (`user_model.py`): Queries database for user
5. **Response**: Access token in body, refresh token in HttpOnly cookie

---

## 3. Database Layer

### 3.1 Database Configuration

**File**: `db/database.py`

```python
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/app.db")
```

This module configures the SQLAlchemy database connection:

| Component | Description |
|-----------|-------------|
| `DATABASE_URL` | Connection string (defaults to SQLite for development) |
| `engine` | SQLAlchemy engine instance |
| `SessionLocal` | Session factory for database operations |
| `Base` | Declarative base for model inheritance |

**SQLite-specific Configuration**:
```python
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
```

This allows SQLite to be used in multi-threaded environments like FastAPI.

### 3.2 Session Management

**File**: `db/session.py`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Purpose**: FastAPI dependency that provides database sessions to route handlers.

**Behavior**:
- Creates a new session for each request
- Automatically closes the session after the request completes
- Used with `Depends(get_db)` in route parameters

---

## 4. Models

### 4.1 User Model

**File**: `models/user_model.py`

The User model represents registered users in the system.

**Table**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique user identifier |
| `email` | String | Unique, Indexed | User's email address |
| `password` | String | Required | Argon2-hashed password |
| `role` | String | Default: "user" | User role (user/admin) |

**Methods**:

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `get_by_id` | Static | `db`, `user_id: int` | `User \| None` | Find user by primary key |
| `get_by_email` | Static | `db`, `email: str` | `User \| None` | Find user by email address |
| `save` | Instance | `db` | `User` | Persist user to database |

**Usage Example**:
```python
# Find user by email
user = User.get_by_email(db, "user@example.com")

# Create new user
new_user = User(email="new@example.com", password=hashed_password)
new_user.save(db)
```

---

### 4.2 RefreshToken Model

**File**: `models/refresh_token.py`

The RefreshToken model manages long-lived tokens for session persistence.

**Table**: `refresh_tokens`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique token identifier |
| `token` | String(255) | Unique, Indexed, Not Null | The actual token value |
| `user_id` | Integer | Foreign Key → users.id | Token owner |
| `expires_at` | DateTime(timezone=True) | Not Null | Token expiration timestamp |
| `revoked` | Boolean | Default: False | Whether token has been invalidated |
| `created_at` | DateTime(timezone=True) | Auto-set | Token creation timestamp |

**Methods**:

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `generate_token` | Static | None | `str` | Creates 64-byte URL-safe random token |
| `get_by_token` | Static | `db`, `token: str` | `RefreshToken \| None` | Find non-revoked token |
| `revoke_all_for_user` | Static | `db`, `user_id: int` | None | Invalidate all tokens for user |
| `save` | Instance | `db` | `RefreshToken` | Persist token to database |
| `revoke` | Instance | `db` | None | Mark single token as revoked |

**Token Generation**:
```python
token = secrets.token_urlsafe(64)  # 86 characters, cryptographically secure
```

**Security Features**:
- Tokens are stored as-is (not hashed) but are cryptographically random
- `revoked` flag allows immediate invalidation without deletion
- `revoke_all_for_user` supports password change security requirement

---

### 4.3 Todo Model

**File**: `models/todo.py`

The Todo model represents user tasks.

**Table**: `todos`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique todo identifier |
| `title` | String(255) | Not Null | Task title |
| `description` | String(1000) | Nullable | Optional task description |
| `completed` | Boolean | Default: False | Completion status |
| `user_id` | Integer | Foreign Key → users.id | Todo owner |
| `created_at` | DateTime(timezone=True) | Auto-set on create | Creation timestamp |
| `updated_at` | DateTime(timezone=True) | Auto-set on update | Last modification timestamp |

**Relationships**:
```python
user = relationship("User", backref="todos")
```
- Each todo belongs to one user
- Users can access their todos via `user.todos`

**Methods**:

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `get_by_id` | Static | `db`, `todo_id: int` | `Todo \| None` | Find todo by ID |
| `get_by_user` | Static | `db`, `user_id: int` | `List[Todo]` | Get all todos for user |
| `save` | Instance | `db` | `Todo` | Create or update todo |
| `delete` | Instance | `db` | None | Remove todo from database |

---

## 5. Schemas (Pydantic Models)

Pydantic schemas handle request/response validation and serialization.

### 5.1 User Schemas

**File**: `schemas/user_schema.py`

#### UserCreate
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
```
**Purpose**: Validates user registration input.
- `EmailStr` enforces valid email format
- Used internally after passing through `UserValidationSchema`

#### UserResponse
```python
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
```
**Purpose**: API response for user data.
- Excludes sensitive fields (password, role)
- `from_attributes = True` enables SQLAlchemy model conversion

#### UserLogin
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```
**Purpose**: Validates login credentials.

#### Token
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```
**Purpose**: Access token response structure.

---

### 5.2 Todo Schemas

**File**: `schemas/todo_schema.py`

#### TodoCreate
```python
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
```
**Purpose**: Validates new todo creation.
- `title` is required
- `description` is optional

#### TodoUpdate
```python
class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```
**Purpose**: Partial update support.
- All fields optional for PATCH-like behavior
- Only provided fields are updated

#### TodoResponse
```python
class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```
**Purpose**: Complete todo representation for API responses.

---

## 6. Services (Business Logic)

Services contain core business logic, independent of HTTP concerns.

### 6.1 UserService

**File**: `services/user_service.py`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_user` | `payload: UserCreate`, `db` | `User` | Register new user |
| `get_user_by_id` | `user_id: int`, `db` | `User` | Retrieve user by ID |
| `authenticate_user` | `email: str`, `password: str`, `db` | `User \| False` | Validate credentials |

#### create_user
```python
def create_user(self, payload: UserCreate, db):
    existing_user = User.get_by_email(db, payload.email)
    if existing_user:
        raise UserAlreadyExistsError(f"User with email {payload.email} already exists")
    
    hashed_password = hash_password(payload.password)
    user = User(email=payload.email, password=hashed_password)
    return user.save(db)
```

**Process**:
1. Check for existing email (prevent duplicates)
2. Hash password with Argon2
3. Create and save user record

#### authenticate_user
```python
def authenticate_user(self, email: str, password: str, db):
    user = User.get_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
```

**Security**: Returns `False` for both "user not found" and "wrong password" to prevent user enumeration attacks.

---

### 6.2 TodoService

**File**: `services/todo_service.py`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_todo` | `user_id`, `todo_data`, `db` | `Todo` | Create new todo |
| `get_todos_by_user` | `user_id`, `db` | `List[Todo]` | List user's todos |
| `get_todo_by_id` | `todo_id`, `db` | `Todo` | Get single todo |
| `update_todo` | `todo_id`, `todo_data`, `db` | `Todo` | Update todo fields |
| `delete_todo` | `todo_id`, `db` | `None` | Remove todo |

#### update_todo
```python
def update_todo(self, todo_id: int, todo_data: TodoUpdate, db: Session) -> Todo:
    todo = self.get_todo_by_id(todo_id, db)
    
    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.completed is not None:
        todo.completed = todo_data.completed
    
    return todo.save(db)
```

**Partial Updates**: Only modifies fields that are explicitly provided in the request.

---

## 7. Controllers

Controllers orchestrate operations between routes and services, handling HTTP-specific concerns.

### 7.1 UserController

**File**: `controllers/user_controller.py`

#### Methods

| Method | Parameters | Returns | Raises | Description |
|--------|------------|---------|--------|-------------|
| `create_user` | `user`, `db` | `UserResponse` | 400, 500 | Register user |
| `get_user_by_id` | `user_id`, `db` | `User` | 404 | Fetch user |
| `login_user` | `user`, `db` | `Token` | 401 | Authenticate and generate tokens |
| `refresh_access_token` | `refresh_token_str`, `db` | `dict` | 401 | Issue new access token |
| `logout_user` | `refresh_token_str`, `db` | `dict` | None | Revoke refresh token |

#### login_user (Authentication Flow)
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

#### refresh_access_token (Token Refresh Flow)
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

**Timezone Handling**: The code handles both timezone-aware and timezone-naive datetime objects for backward compatibility with existing tokens.

---

### 7.2 TodoController

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

## 8. API Routes

### 8.1 User Routes

**File**: `api/v1/routes/user_routes.py`

**Prefix**: `/api/v1/users`

#### Cookie Configuration
```python
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds
```

#### Endpoints

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| POST | `/register` | No | Create new user account |
| POST | `/login` | No | Authenticate and get tokens |
| POST | `/refresh` | No (cookie) | Get new access token |
| POST | `/logout` | No (cookie) | Revoke refresh token |
| GET | `/{user_id}` | Yes | Get user details |

#### Login Endpoint (Cookie Handling)
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

**Security Settings**:
| Setting | Value | Purpose |
|---------|-------|---------|
| `httponly` | True | Prevents XSS attacks from reading cookie |
| `secure` | False (dev) | Set True for HTTPS in production |
| `samesite` | "lax" | CSRF protection while allowing navigation |
| `path` | "/" | Cookie sent with all requests |

---

### 8.2 Todo Routes

**File**: `api/v1/routes/todo_routes.py`

**Prefix**: `/api/v1/todos`

All routes require JWT authentication (enforced by middleware).

#### User ID Extraction
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

#### Endpoints

| Method | Path | Auth Required | Role | Description |
|--------|------|---------------|------|-------------|
| POST | `/` | Yes | Any | Create todo |
| GET | `/` | Yes | Any | List user's todos |
| GET | `/{todo_id}` | Yes | Any | Get single todo |
| PUT | `/{todo_id}` | Yes | Any | Update todo |
| DELETE | `/{todo_id}` | Yes | Admin | Delete todo |

#### Admin-Only Delete
```python
@router.delete("/{todo_id}", status_code=204, dependencies=[Depends(RoleChecker(["admin"]))])
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    controller.delete_todo(todo_id, db)
    return None
```

---

## 9. Middlewares

### 9.1 JWT Authentication Middleware

**File**: `middlewares/jwt_middleware.py`

Global middleware that protects all routes except explicitly excluded paths.

```python
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_paths = [
            "/docs", "/openapi.json", "/health",
            "/api/v1/users/login", "/api/v1/users/register",
            "/api/v1/users/refresh", "/api/v1/users/logout"
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

**Features**:
- Path normalization handles trailing slash variations
- Stores decoded JWT payload in `request.state.user`
- Returns JSON errors with proper status codes

---

### 9.2 Role Checker

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

**Usage**:
```python
@router.delete("/", dependencies=[Depends(RoleChecker(["admin"]))])
def admin_only_function():
    pass
```

---

### 9.3 User Validation Schema

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

**Password Requirements**:
- Minimum 8 characters
- Maximum 30 characters
- Alphanumeric only (a-z, A-Z, 0-9)

---

## 10. Utilities

### 10.1 JWT Handler

**File**: `utils/jwt_handler.py`

#### Configuration
```python
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `create_access_token` | `data: dict`, `expires_delta: Optional[timedelta]` | `str` | Generate JWT access token |
| `verify_token` | `token: str` | `Optional[dict]` | Decode and validate JWT |
| `get_refresh_token_expiry` | None | `datetime` | Calculate refresh token expiry |

#### create_access_token
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### verify_token
```python
def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
```

**Error Handling**: Returns `None` for any JWT error instead of raising exceptions, allowing graceful handling in middleware.

---

### 10.2 Password Hashing

**File**: `utils/hash_generator.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Why Argon2?**
- Winner of the Password Hashing Competition (2015)
- Memory-hard algorithm resistant to GPU attacks
- Recommended by OWASP for password storage

---

### 10.3 Custom Exceptions

**File**: `utils/exceptions.py`

```python
class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass
```

Used for clean error handling in services, converted to HTTP errors in controllers.

---

## 11. Authentication System

### Token Flow Diagram

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

### Token Comparison

| Aspect | Access Token | Refresh Token |
|--------|--------------|---------------|
| Lifetime | 30 minutes | 7 days |
| Storage | Client memory / localStorage | HttpOnly cookie |
| Purpose | API authentication | Obtain new access tokens |
| Can be stolen via XSS? | Yes (if in localStorage) | No (HttpOnly) |
| Revocable? | No (stateless) | Yes (database check) |

---

## 12. API Endpoints Reference

### User Endpoints

#### POST /api/v1/users/register
Create a new user account.

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
    "id": 1,
    "email": "user@example.com"
}
```

**Errors**:
- 400: User already exists
- 422: Validation error (invalid email or password format)

---

#### POST /api/v1/users/login
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

#### POST /api/v1/users/refresh
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

#### POST /api/v1/users/logout
Revoke refresh token and clear cookie.

**Response** (200):
```json
{
    "message": "Successfully logged out"
}
```

---

### Todo Endpoints

All todo endpoints require `Authorization: Bearer {access_token}` header.

#### POST /api/v1/todos/
Create a new todo.

**Request Body**:
```json
{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
}
```

**Response** (200):
```json
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": 1,
    "created_at": "2024-01-19T10:00:00Z",
    "updated_at": null
}
```

---

#### GET /api/v1/todos/
List all todos for authenticated user.

**Response** (200):
```json
[
    {
        "id": 1,
        "title": "Buy groceries",
        "completed": false,
        ...
    }
]
```

---

#### PUT /api/v1/todos/{todo_id}
Update a todo (partial update supported).

**Request Body**:
```json
{
    "completed": true
}
```

---

#### DELETE /api/v1/todos/{todo_id}
Delete a todo. **Admin only**.

**Response**: 204 No Content

**Errors**:
- 403: Access denied (not admin)
- 404: Todo not found

---

## 13. Testing Guide

### Manual Testing with cURL

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 2. Login (save cookies)
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  -c cookies.txt

# 3. Create todo (use access token from login response)
curl -X POST http://localhost:8000/api/v1/todos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"title": "Test todo"}'

# 4. Refresh token
curl -X POST http://localhost:8000/api/v1/users/refresh \
  -b cookies.txt

# 5. Logout
curl -X POST http://localhost:8000/api/v1/users/logout \
  -b cookies.txt
```
### Running the pre-written tests
```
# From project root
pytest

# With verbose output
pytest -v

# With print statements visible
pytest -v -s
```

---

## 14. Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./app.db` | Database connection string |
| `SECRET_KEY` | `supersecretkey` | JWT signing key (change in production!) |

### Running the Application

```bash
# Development
uvicorn index:app --reload

# Production
uvicorn index:app --host 0.0.0.0 --port 8000

# Docker
docker-compose up
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Summary

This FastAPI application demonstrates a production-ready architecture with:

- **Clean separation of concerns** through layered architecture
- **Secure authentication** using JWT access/refresh token pattern
- **Role-based authorization** for admin-only operations
- **Input validation** via Pydantic schemas
- **Password security** with Argon2 hashing
- **Database abstraction** through SQLAlchemy ORM
- **Schema versioning** with Alembic migrations
- **Containerization** support with Docker

The codebase is maintainable, testable, and follows Python best practices.

---

## 15. Docker Deployment

### 15.1 Dockerfile

The application includes a production-ready Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build Process Explained**:

1. **Base Image**: Uses `python:3.10-slim` for a minimal footprint (~150MB vs ~900MB for full image)
2. **Dependency Installation**: Copies `requirements.txt` first to leverage Docker layer caching
3. **No-cache-dir**: Reduces image size by not caching pip packages
4. **Host Binding**: Uses `0.0.0.0` to accept connections from outside the container

### 15.2 Docker Compose

The `docker-compose.yml` provides multi-container orchestration:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - SECRET_KEY=${SECRET_KEY:-your-production-secret}
    volumes:
      - ./app.db:/app/app.db
    restart: unless-stopped

  # Optional: PostgreSQL for production
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: fastapi
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
```

**Docker Commands**:

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up --build --force-recreate
```

### 15.3 Production Considerations

When deploying to production, consider these Docker best practices:

| Aspect | Development | Production |
|--------|-------------|------------|
| Debug mode | Enabled | Disabled |
| Secret key | Default value | Strong random value |
| Database | SQLite | PostgreSQL/MySQL |
| HTTPS | Not required | Required (use reverse proxy) |
| Logging | Console | Centralized logging service |
| Health checks | Optional | Required |

**Production Dockerfile Additions**:
```dockerfile
# Add health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

---

## 16. Security Best Practices

### 16.1 Authentication Security

The application implements several security measures:

**Password Storage**:
- Uses Argon2 hashing algorithm (PHC winner)
- Automatic salting (unique per password)
- Configurable work factors for future-proofing

**JWT Token Security**:
- Short-lived access tokens (30 minutes)
- Refresh tokens stored in HttpOnly cookies
- Token payload includes user role for authorization
- Tokens are signed with HS256 algorithm

**Recommended Production Changes**:

```python
# In utils/jwt_handler.py
SECRET_KEY = os.getenv("SECRET_KEY")  # Remove default value
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# Use RS256 for production (asymmetric signing)
ALGORITHM = "RS256"
```

### 16.2 Cookie Security

Current cookie settings and recommendations:

| Setting | Current | Production Recommendation |
|---------|---------|---------------------------|
| `httponly` | True | True (prevents XSS) |
| `secure` | False | True (HTTPS only) |
| `samesite` | "lax" | "strict" (stricter CSRF protection) |
| `domain` | None | Set to your domain |

**Production Cookie Configuration**:
```python
response.set_cookie(
    key=REFRESH_TOKEN_COOKIE_NAME,
    value=tokens["refresh_token"],
    max_age=REFRESH_TOKEN_MAX_AGE,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="strict",
    domain=".yourdomain.com"
)
```

### 16.3 Input Validation

The application validates input at multiple layers:

1. **Pydantic Schemas**: Type validation and constraints
2. **Custom Validators**: Password complexity rules
3. **Database Constraints**: Unique email enforcement

**Password Validation Rules** (in `auth_validate.py`):
```python
@field_validator('password')    
@classmethod
def validate_password(cls, v):
    if not re.match(r'^[a-zA-Z0-9]{8,30}$', v):
        raise ValueError("Password must be between 8 and 30 characters...")
    return v
```

**Recommended Enhancements**:
- Add rate limiting for login attempts
- Implement account lockout after failed attempts
- Add CAPTCHA for registration
- Log authentication failures for monitoring

### 16.4 SQL Injection Prevention

SQLAlchemy ORM provides protection against SQL injection by using parameterized queries:

```python
# Safe: Uses parameterized query
User.get_by_email(db, email)

# Under the hood:
db.query(User).filter(User.email == email).first()
# Generates: SELECT * FROM users WHERE email = ?
```

Never use raw SQL with string interpolation:
```python
# DANGEROUS - Never do this!
db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

---

## 17. Error Handling Patterns

### 17.1 Exception Hierarchy

The application uses a layered exception handling approach:

```
┌─────────────────────────────────────────┐
│           Route Layer                    │
│   Returns HTTPException to client        │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Controller Layer                 │
│   Catches service exceptions,            │
│   converts to HTTPException              │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│          Service Layer                   │
│   Raises custom domain exceptions        │
│   (UserNotFoundError, etc.)              │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│           Model Layer                    │
│   Returns None for not found,            │
│   raises DB exceptions for errors        │
└─────────────────────────────────────────┘
```

### 17.2 Custom Exceptions

**File**: `utils/exceptions.py`

```python
class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""
    pass

class UserNotFoundError(Exception):
    """Raised when a user cannot be found by ID or email."""
    pass
```

**Usage Pattern**:
```python
# In Service
def get_user_by_id(self, user_id: int, db):
    user = User.get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found")
    return user

# In Controller
def get_user_by_id(self, user_id: int, db):
    try:
        return self.userService.get_user_by_id(user_id, db)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 17.3 Global Exception Handler

The application includes a custom validation error handler:

```python
@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc):
    errors = [{
        "field": ".".join(str(loc) for loc in e["loc"]), 
        "message": e["msg"]
    } for e in exc.errors()]
    return JSONResponse(
        status_code=422, 
        content={"detail": "Validation error", "errors": errors}
    )
```

**Response Format**:
```json
{
    "detail": "Validation error",
    "errors": [
        {
            "field": "body.email",
            "message": "value is not a valid email address"
        }
    ]
}
```

### 17.4 HTTP Status Codes Used

| Status Code | Meaning | Used For |
|-------------|---------|----------|
| 200 | OK | Successful GET, POST, PUT |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | User already exists |
| 401 | Unauthorized | Invalid/missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Unexpected server errors |

---

## 18. Troubleshooting Guide

### 18.1 Common Issues and Solutions

#### Issue: "Refresh token not found" on POST /refresh

**Cause**: The refresh token cookie is not being sent with the request.

**Solutions**:
1. Ensure you logged in first to receive the cookie
2. Check cookie path matches request URL
3. In Postman: Verify cookies are enabled for the domain
4. In curl: Use `-b cookies.txt` to send saved cookies

**Debug Command**:
```bash
# Check what cookies are being sent
curl -v -X POST http://localhost:8000/api/v1/users/refresh -b cookies.txt
# Look for "Cookie:" header in the request output
```

#### Issue: "Internal Server Error" on refresh endpoint

**Cause**: Timezone mismatch when comparing datetime objects.

**Solution**: Ensure all datetime comparisons use timezone-aware objects:
```python
# Correct
from datetime import datetime, timezone
now = datetime.now(timezone.utc)

# If database value is naive, convert it
if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=timezone.utc)
```

#### Issue: "405 Method Not Allowed" on POST requests

**Cause**: Trailing slash redirect converting POST to GET.

**Solution**: 
- Use URLs without trailing slashes: `/api/v1/users/refresh` (not `/refresh/`)
- Or configure FastAPI to handle trailing slashes:
```python
app = FastAPI(redirect_slashes=False)
```

#### Issue: Token expires immediately after login

**Cause**: Clock skew between server and token verification.

**Solution**: Ensure system clocks are synchronized using NTP.

#### Issue: CORS errors in browser

**Cause**: Missing CORS configuration for frontend domain.

**Solution**: Add CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 18.2 Debugging Tools

**Enable SQL Logging**:
```python
# In db/database.py
engine = create_engine(DATABASE_URL, echo=True)  # Logs all SQL
```

**View Current User in Route**:
```python
@router.get("/debug")
def debug_user(request: Request):
    return {"user": getattr(request.state, "user", None)}
```

**Inspect JWT Token**:
```bash
# Decode JWT (without verification) at jwt.io or:
echo "YOUR_TOKEN" | cut -d'.' -f2 | base64 -d
```

---

## 19. Development Workflow

### 19.1 Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd fastapi-bootcamp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn index:app --reload
```

### 19.2 Adding New Features

**Example: Adding a new endpoint**

1. **Define Schema** (`schemas/new_schema.py`):
```python
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    name: str
    value: int
```

2. **Create Model** (`models/new_model.py`):
```python
from sqlalchemy import Column, Integer, String
from db.database import Base

class NewModel(Base):
    __tablename__ = "new_features"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

3. **Create Migration**:
```bash
alembic revision --autogenerate -m "add new_features table"
alembic upgrade head
```

4. **Create Service** (`services/new_service.py`):
```python
class NewService:
    def create(self, data, db):
        # Business logic here
        pass
```

5. **Create Controller** (`controllers/new_controller.py`):
```python
class NewController:
    def __init__(self):
        self.service = NewService()
```

6. **Create Routes** (`api/v1/routes/new_routes.py`):
```python
from fastapi import APIRouter
router = APIRouter()

@router.post("/")
def create_new():
    pass
```

7. **Register Router** (`index.py`):
```python
from api.v1.routes.new_routes import router as new_router
app.include_router(new_router, prefix="/api/v1/new", tags=["New Feature"])
```

### 19.3 Code Style Guidelines

The project follows PEP 8 with these conventions:

- **Imports**: Standard library, third-party, local (separated by blank lines)
- **Class Names**: PascalCase (`UserController`)
- **Function Names**: snake_case (`create_user`)
- **Constants**: UPPER_CASE (`SECRET_KEY`)
- **Type Hints**: Used for function signatures
- **Docstrings**: Triple-quoted strings for public functions

**Running Code Quality Tools**:
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Lint
flake8 .
```

---

## 20. Conclusion

This FastAPI Bootcamp project demonstrates a complete, production-ready REST API implementation with:

### Key Achievements

1. **Robust Authentication System**
   - Dual-token architecture (access + refresh)
   - Secure cookie-based refresh token storage
   - Role-based access control

2. **Clean Architecture**
   - Clear separation between layers
   - Dependency injection pattern
   - Reusable service components

3. **Security First Approach**
   - Argon2 password hashing
   - HttpOnly cookies for sensitive tokens
   - Input validation at multiple layers
   - Protection against common vulnerabilities

4. **Developer Experience**
   - Automatic API documentation (Swagger UI)
   - Database migrations with Alembic
   - Docker support for easy deployment
   - Comprehensive error handling

### Future Enhancements

Consider adding these features for a more complete application:

- **Rate Limiting**: Protect against brute force attacks
- **Email Verification**: Confirm user email ownership
- **Password Reset**: Secure password recovery flow
- **OAuth2 Social Login**: Google, GitHub integration
- **API Versioning Strategy**: Support multiple API versions
- **Caching Layer**: Redis for session and response caching
- **Background Tasks**: Celery for async operations
- **Monitoring**: Prometheus metrics and health endpoints
- **Logging**: Structured logging with correlation IDs

This documentation serves as both a learning resource and a reference guide for maintaining and extending the application. The patterns demonstrated here can be applied to any FastAPI project requiring user authentication and CRUD operations.
