# Services (Business Logic)

Services contain core business logic, independent of HTTP concerns.

---

## UserService

**File**: `services/user_service.py`

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_user` | `payload: UserCreate`, `db` | `User` | Register new user |
| `get_user_by_id` | `user_id: int`, `db` | `User` | Retrieve user by ID |
| `authenticate_user` | `email: str`, `password: str`, `db` | `User \| False` | Validate credentials |

### create_user

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

### authenticate_user

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

## TodoService

**File**: `services/todo_service.py`

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_todo` | `user_id`, `todo_data`, `db` | `Todo` | Create new todo |
| `get_todos_by_user` | `user_id`, `db` | `List[Todo]` | List user's todos |
| `get_todo_by_id` | `todo_id`, `db` | `Todo` | Get single todo |
| `update_todo` | `todo_id`, `todo_data`, `db` | `Todo` | Update todo fields |
| `delete_todo` | `todo_id`, `db` | `None` | Remove todo |

### update_todo

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

[← Back to Index](./README.md) | [Previous: Schemas](./04-schemas.md) | [Next: Controllers →](./06-controllers.md)
