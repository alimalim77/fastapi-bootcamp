# FastAPI Clean Architecture

A production-ready FastAPI application with JWT authentication, OTP email verification, role-based access control, and Docker support.

[![Docker Image](https://img.shields.io/docker/v/alimalim77/fastapi-bootcamp?label=Docker%20Hub)](https://hub.docker.com/r/alimalim77/fastapi-bootcamp)

## Features

- 🔐 **JWT Authentication** - Access + Refresh tokens with HttpOnly cookies
- 📧 **OTP Email Verification** - Secure registration with 6-digit codes
- 👮 **Role-Based Access Control** - Admin/User permissions
- 🗄️ **Database Migrations** - Alembic for schema versioning
- 🐳 **Docker Support** - Production-ready containerization

## Quick Start

### Docker (Recommended)

```bash
# Pull and run
docker pull alimalim77/fastapi-bootcamp:latest
docker compose up
```

### Local Development

```bash
# Clone and setup
git clone https://github.com/alimalim77/fastapi-bootcamp.git
cd fastapi-bootcamp

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install and run
pip install -r requirements.txt
alembic upgrade head
uvicorn index:app --reload
```

### Access the API

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API Base |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

## Configuration

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
```

## 📚 Documentation

Full documentation is available in the [`docs/`](./docs/) folder:

- [Architecture](./docs/01-architecture.md) - Project structure & layers
- [Authentication](./docs/08-authentication.md) - JWT token flow
- [OTP Verification](./docs/10-otp-verification.md) - Email verification
- [API Reference](./docs/12-api-reference.md) - Complete endpoints
- [Configuration](./docs/14-configuration.md) - Environment & Docker

**[→ View Full Documentation Index](./docs/README.md)**

## Tech Stack

FastAPI • SQLAlchemy • Alembic • JWT • Argon2 • Docker

## License

MIT License

## Author

**Ali Malim** - [GitHub](https://github.com/alimalim77)
