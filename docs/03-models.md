# Models

SQLAlchemy models represent database tables and provide data access methods.

---

## User Model

**File**: `models/user_model.py`

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

## RefreshToken Model

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

## Todo Model

**File**: `models/todo.py`

**Table**: `todos`

### Priority Enum

The `Priority` enum defines task importance levels:

| Value | Description |
|-------|-------------|
| `HIGH` | High priority task |
| `MEDIUM` | Medium priority (default) |
| `LOW` | Low priority task |

```python
class Priority(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique todo identifier |
| `title` | String(255) | Not Null | Task title |
| `description` | String(1000) | Nullable | Optional task description |
| `completed` | Boolean | Default: False | Completion status |
| `priority` | Enum(Priority) | Default: MEDIUM, Not Null | Task priority level |
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

## PendingRegistration Model

**File**: `models/pending_registration.py`

Stores pending user registrations awaiting OTP verification.

**Table**: `pending_registrations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique identifier |
| `email` | String | Unique, Indexed, Not Null | Email awaiting verification |
| `hashed_password` | String | Not Null | Pre-hashed password (Argon2) |
| `otp_hash` | String | Not Null | SHA-256 hash of the OTP |
| `expires_at` | DateTime | Not Null | OTP expiration timestamp |
| `created_at` | DateTime | Auto-set | Record creation timestamp |

**Methods**:

| Method | Type | Parameters | Returns | Description |
|--------|------|------------|---------|-------------|
| `generate_otp` | Static | None | `str` | Generate random 6-digit OTP |
| `hash_otp` | Static | `otp: str` | `str` | SHA-256 hash of OTP |
| `verify_otp` | Instance | `otp: str` | `bool` | Compare OTP against stored hash |
| `is_expired` | Instance | None | `bool` | Check if OTP has expired |
| `get_expiry_time` | Static | `minutes: int = 10` | `datetime` | Calculate expiration timestamp |
| `get_by_id` | Static | `db`, `registration_id` | `PendingRegistration \| None` | Find by ID |
| `get_by_email` | Static | `db`, `email: str` | `PendingRegistration \| None` | Find by email |
| `save` | Instance | `db` | `PendingRegistration` | Persist to database |
| `delete` | Instance | `db` | None | Remove from database |
| `update_otp` | Instance | `db`, `new_otp: str` | `PendingRegistration` | Regenerate OTP |

> See [OTP Verification](./10-otp-verification.md) for complete OTP flow documentation.

---

[← Back to Index](./README.md) | [Previous: Database](./02-database.md) | [Next: Schemas →](./04-schemas.md)
