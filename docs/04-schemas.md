# Schemas (Pydantic Models)

Pydantic schemas handle request/response validation and serialization.

---

## User Schemas

**File**: `schemas/user_schema.py`

### UserCreate
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
```
**Purpose**: Validates user registration input.
- `EmailStr` enforces valid email format
- Used internally after passing through `UserValidationSchema`

### UserResponse
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

### UserLogin
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```
**Purpose**: Validates login credentials.

### Token
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```
**Purpose**: Access token response structure.

### RegisterResponse
```python
class RegisterResponse(BaseModel):
    message: str                    # "Verification code sent to your email"
    pending_registration_id: int    # ID for verify-otp call
```
**Purpose**: Response after initiating OTP registration.

### OTPVerifyRequest
```python
class OTPVerifyRequest(BaseModel):
    pending_registration_id: int    # From register response
    otp: str                        # 6-digit code from email
```
**Purpose**: Request to verify OTP and complete registration.

---

## Todo Schemas

**File**: `schemas/todo_schema.py`

### TodoCreate
```python
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
```
**Purpose**: Validates new todo creation.
- `title` is required
- `description` is optional

### TodoUpdate
```python
class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
```
**Purpose**: Partial update support.
- All fields optional for PATCH-like behavior
- Only provided fields are updated

### TodoResponse
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

[← Back to Index](./README.md) | [Previous: Models](./03-models.md) | [Next: Services →](./05-services.md)
