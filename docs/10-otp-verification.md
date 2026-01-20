# OTP Verification Module

Email-based OTP verification for secure user registration.

---

## Registration Flow Diagram

```
    ┌──────────────┐
    │    Client    │
    └──────┬───────┘
           │ 1. POST /register {email, password}
           ▼
    ┌──────────────────────────────────────┐
    │   Server                             │
    │  - Check if email already registered │
    │  - Generate 6-digit OTP              │
    │  - Hash OTP and store with email     │
    │  - Send OTP to email                 │
    └──────┬───────────────────────────────┘
           │ 2. Response: {pending_registration_id, message}
           ▼
    ┌──────────────┐
    │    Client    │
    │ - User checks│
    │   email inbox│
    └──────┬───────┘
           │ 3. POST /verify-otp {pending_registration_id, otp}
           ▼
    ┌──────────────────────────────────────┐
    │   Server                             │
    │  - Lookup pending registration       │
    │  - Verify OTP hash                   │
    │  - Check expiration (10 min)         │
    │  - Create actual user account        │
    │  - Delete pending registration       │
    └──────┬───────────────────────────────┘
           │ 4. Response: {id, email}
           ▼
    ┌──────────────┐
    │ User Created │
    │ Can login now│
    └──────────────┘
```

---

## PendingRegistration Model

**File**: `models/pending_registration.py`

**Table**: `pending_registrations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique identifier |
| `email` | String | Unique, Indexed, Not Null | Email awaiting verification |
| `hashed_password` | String | Not Null | Pre-hashed password (Argon2) |
| `otp_hash` | String | Not Null | SHA-256 hash of the OTP |
| `expires_at` | DateTime | Not Null | OTP expiration timestamp |
| `created_at` | DateTime | Auto-set | Record creation timestamp |

### Methods

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `generate_otp` | Static | None | `str` | Generate random 6-digit OTP (100000-999999) |
| `hash_otp` | Static | `otp: str` | `str` | SHA-256 hash of OTP for secure storage |
| `verify_otp` | Instance | `otp: str` | `bool` | Compare provided OTP against stored hash |
| `is_expired` | Instance | None | `bool` | Check if OTP has expired |
| `get_expiry_time` | Static | `minutes: int = 10` | `datetime` | Calculate expiration timestamp |
| `get_by_id` | Static | `db`, `registration_id: int` | `PendingRegistration \| None` | Find by ID |
| `get_by_email` | Static | `db`, `email: str` | `PendingRegistration \| None` | Find by email |
| `save` | Instance | `db` | `PendingRegistration` | Persist to database |
| `delete` | Instance | `db` | None | Remove from database |
| `update_otp` | Instance | `db`, `new_otp: str` | `PendingRegistration` | Regenerate OTP for resend |

### OTP Generation

```python
def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)  # Always 6 digits
```

---

## Email Sender Utility

**File**: `utils/email_sender.py`

### send_otp_email

```python
def send_otp_email(to_email: str, otp_code: str) -> bool:
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `to_email` | str | Recipient email address |
| `otp_code` | str | The 6-digit OTP to send |

**Returns**: `True` if email sent successfully

**Raises**: 
- `ValueError` if environment variables not configured
- SMTP exceptions if email delivery fails

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `EMAIL_ADDRESS` | Gmail sender address |
| `EMAIL_PASSWORD` | Gmail App Password (not regular password) |

### Email Format

- Sends both plain text and HTML versions
- HTML version includes styled verification code display
- Code displayed prominently with 10-minute expiry notice

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Google Account
2. Go to Google Account → Security → App Passwords
3. Generate new app password for "Mail"
4. Use this 16-character password as `EMAIL_PASSWORD`

---

## Controller Methods

**File**: `controllers/user_controller.py`

### initiate_registration

```python
def initiate_registration(self, email: str, password: str, db) -> RegisterResponse:
```

**Process**:
1. Check if email already registered → 400 if exists
2. Check for existing pending registration
3. If pending exists: regenerate OTP and update expiry
4. If new: hash password, generate OTP, create pending registration
5. Send OTP email → 500 if email fails
6. Return `pending_registration_id` for verification step

**Edge Case Handling**:
- If user calls `/register` again before verifying, a new OTP is sent
- Old OTP becomes invalid when new one is generated

### verify_otp

```python
def verify_otp(self, pending_registration_id: int, otp: str, db) -> UserResponse:
```

**Process**:
1. Lookup pending registration by ID → 404 if not found
2. Check expiration → 400 if expired (auto-deletes record)
3. Verify OTP hash → 400 if invalid
4. Create actual User with pre-hashed password
5. Delete pending registration
6. Return created user

---

## Schemas

**File**: `schemas/user_schema.py`

### RegisterResponse

```python
class RegisterResponse(BaseModel):
    message: str                    # "Verification code sent to your email"
    pending_registration_id: int    # ID for verify-otp call
```

### OTPVerifyRequest

```python
class OTPVerifyRequest(BaseModel):
    pending_registration_id: int    # From register response
    otp: str                        # 6-digit code from email
```

---

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| OTP Storage | SHA-256 hashed, never plaintext |
| OTP Length | 6 digits (100,000 - 999,999) |
| OTP Expiry | 10 minutes from generation |
| Rate Limiting | Resend generates new OTP (old invalidated) |
| Password Pre-Hash | Password hashed (Argon2) before pending storage |
| Email Delivery | SMTP over SSL (port 465) |

---

## Database Migration

Migration file: `alembic/versions/xxx_add_pending_registrations_table.py`

```python
def upgrade() -> None:
    op.create_table('pending_registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('otp_hash', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pending_registrations_email', 'pending_registrations', ['email'], unique=True)
    op.create_index('ix_pending_registrations_id', 'pending_registrations', ['id'], unique=False)
```

---

[← Back to Index](./README.md) | [Previous: Authorization](./09-authorization.md) | [Next: Utilities →](./11-utilities.md)
