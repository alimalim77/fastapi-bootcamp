# FastAPI Bootcamp Documentation

A comprehensive REST API built with FastAPI following clean architecture principles.

## 📚 Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Architecture](./01-architecture.md) | Project overview, structure, and layer design |
| 2 | [Database](./02-database.md) | Database configuration and session management |
| 3 | [Models](./03-models.md) | SQLAlchemy models (User, Todo, RefreshToken, PendingRegistration) |
| 4 | [Schemas](./04-schemas.md) | Pydantic request/response schemas |
| 5 | [Services](./05-services.md) | Business logic layer |
| 6 | [Controllers](./06-controllers.md) | Controller layer orchestration |
| 7 | [API Routes](./07-api-routes.md) | Route definitions and handlers |
| 8 | [Authentication](./08-authentication.md) | JWT tokens, login/logout, token refresh |
| 9 | [Authorization](./09-authorization.md) | Middlewares and role-based access control |
| 10 | [OTP Verification](./10-otp-verification.md) | Email OTP registration verification |
| 11 | [Utilities](./11-utilities.md) | JWT handler, password hashing, exceptions |
| 12 | [API Reference](./12-api-reference.md) | Complete API endpoints documentation |
| 13 | [Testing](./13-testing.md) | Testing guide with cURL examples |
| 14 | [Configuration](./14-configuration.md) | Environment variables, Docker, deployment |
| 15 | [Rate Limiting](./15-rate-limiting.md) | Redis-based API rate limiting |

---

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd fastapi-bootcamp
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn index:app --reload
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | SQLite (Dev) / PostgreSQL (Prod) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT (python-jose) |
| Password Hashing | Argon2 (passlib) |
| Validation | Pydantic |
| Rate Limiting | Redis |
| Container | Docker |

## Key Features

- ✅ **OTP Email Verification** - Secure user registration
- ✅ **JWT Authentication** - Access + Refresh tokens
- ✅ **Role-Based Access** - Admin/User permissions
- ✅ **Rate Limiting** - Redis-based API protection
- ✅ **Clean Architecture** - Layered separation
- ✅ **Docker Support** - Production-ready containers

