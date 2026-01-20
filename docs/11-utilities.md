# Utilities

Helper functions and utility modules.

---

## JWT Handler

**File**: `utils/jwt_handler.py`

### Configuration

```python
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `create_access_token` | `data: dict`, `expires_delta: Optional[timedelta]` | `str` | Generate JWT access token |
| `verify_token` | `token: str` | `Optional[dict]` | Decode and validate JWT |
| `get_refresh_token_expiry` | None | `datetime` | Calculate refresh token expiry |

### create_access_token

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

### verify_token

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

## Password Hashing

**File**: `utils/hash_generator.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Why Argon2?

- Winner of the Password Hashing Competition (2015)
- Memory-hard algorithm resistant to GPU attacks
- Recommended by OWASP for password storage

---

## Email Sender

**File**: `utils/email_sender.py`

```python
def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send OTP verification email using Gmail SMTP.
    
    Requires EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.
    EMAIL_PASSWORD should be a Gmail App Password (not your regular password).
    """
```

### SMTP Configuration

| Setting | Value |
|---------|-------|
| Server | smtp.gmail.com |
| Port | 465 (SSL) |
| Security | SMTP_SSL |

### Email Template Features

- Plain text fallback for email clients without HTML
- Styled HTML with prominent OTP display
- 10-minute expiry notice
- Professional design with centered layout

---

## Custom Exceptions

**File**: `utils/exceptions.py`

```python
class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass
```

Used for clean error handling in services, converted to HTTP errors in controllers.

### Usage Example

```python
# In service
if existing_user:
    raise UserAlreadyExistsError(f"User with email {email} already exists")

# In controller
try:
    return self.userService.create_user(user, db)
except UserAlreadyExistsError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

[← Back to Index](./README.md) | [Previous: OTP Verification](./10-otp-verification.md) | [Next: API Reference →](./12-api-reference.md)
