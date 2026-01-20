# Architecture Overview

## Project Overview

This project is a FastAPI-based REST API implementing a **Todo application** with full user authentication. It demonstrates best practices in API development including:

- **Clean Architecture**: Separation of concerns with distinct layers (routes, controllers, services, models)
- **JWT Authentication**: Secure access and refresh token system
- **OTP Email Verification**: Email-based user registration verification
- **Role-Based Access Control**: Admin-only operations protected by middleware
- **Database Migrations**: Alembic for schema versioning
- **Password Security**: Argon2 hashing algorithm
- **Docker Support**: Containerized deployment

---

## Project Structure

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
│   ├── refresh_token.py     # RefreshToken SQLAlchemy model
│   └── pending_registration.py  # OTP pending registrations
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
│   ├── email_sender.py      # OTP email delivery
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

## Layered Architecture

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

---

## Data Flow Example: User Login

1. **Route** (`user_routes.py`): Receives POST `/api/v1/users/login`
2. **Controller** (`user_controller.py`): Validates, calls service, generates tokens
3. **Service** (`user_service.py`): Authenticates user against database
4. **Model** (`user_model.py`): Queries database for user
5. **Response**: Access token in body, refresh token in HttpOnly cookie

---

## Data Flow Example: OTP Registration

1. **Route** (`user_routes.py`): Receives POST `/api/v1/users/register`
2. **Controller** (`user_controller.py`): Creates pending registration, generates OTP
3. **Utility** (`email_sender.py`): Sends OTP to user's email
4. **Route** (`user_routes.py`): Receives POST `/api/v1/users/verify-otp`
5. **Controller** (`user_controller.py`): Verifies OTP, creates user
6. **Response**: User created, can now login

---

[← Back to Index](./README.md) | [Next: Database →](./02-database.md)
