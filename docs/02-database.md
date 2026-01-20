# Database Layer

## Database Configuration

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

---

## Session Management

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

**Usage Example**:
```python
from db.session import get_db
from sqlalchemy.orm import Session

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

## Database Migrations (Alembic)

### Creating a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### Migration Example

```python
def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
```

---

[← Back to Index](./README.md) | [Previous: Architecture](./01-architecture.md) | [Next: Models →](./03-models.md)
