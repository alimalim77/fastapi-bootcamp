# FastAPI Clean Architecture

A production-ready FastAPI application with JWT authentication, role-based access control (RBAC), PostgreSQL database, and Docker support.

[![Docker Image](https://img.shields.io/docker/v/alimalim77/fastapi-bootcamp?label=Docker%20Hub)](https://hub.docker.com/r/alimalim77/fastapi-bootcamp)

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👮 **Role-Based Access Control** - Admin/User roles with protected endpoints
- 🗄️ **Database Migrations** - Alembic for schema versioning
- 🐳 **Docker Support** - Production-ready containerization
- 📚 **API Documentation** - Auto-generated Swagger UI

## Quick Start with Docker (Recommended)

### Option 1: Pull from Docker Hub

```bash
# Pull the image
docker pull alimalim77/fastapi-bootcamp:latest

# Run with PostgreSQL using docker-compose
curl -O https://raw.githubusercontent.com/alimalim77/fastapi-bootcamp/main/docker-compose.yml
docker compose up
```

### Option 2: Clone and Build

```bash
# Clone the repository
git clone https://github.com/alimalim77/fastapi-bootcamp.git
cd fastapi-bootcamp

# Build and run
docker compose up --build
```

### Access the API

Once running:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Local Development Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/alimalim77/fastapi-bootcamp.git
cd fastapi-bootcamp

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn index:app --reload
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` |
| `SECRET_KEY` | JWT signing secret key | `supersecretkey` |

### Example `.env` file

```env
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-super-secret-key-change-in-production
```

For PostgreSQL (Docker):
```env
DATABASE_URL=postgresql://fastapi:fastapi@db:5432/fastapi_db
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/users/register` | Register new user | ❌ |
| `POST` | `/api/v1/users/login` | Login and get JWT token | ❌ |
| `GET` | `/api/v1/users/{id}` | Get user by ID | ✅ |

### Todos

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/todos/` | Create a todo | ✅ |
| `GET` | `/api/v1/todos/` | List all user's todos | ✅ |
| `GET` | `/api/v1/todos/{id}` | Get a specific todo | ✅ |
| `PUT` | `/api/v1/todos/{id}` | Update a todo | ✅ |
| `DELETE` | `/api/v1/todos/{id}` | Delete a todo | ✅ **Admin only** |

---

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create a Todo (Authenticated)

```bash
curl -X POST http://localhost:8000/api/v1/todos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first todo", "description": "Learn FastAPI"}'
```

### 4. List All Todos

```bash
curl http://localhost:8000/api/v1/todos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Project Structure

```
fastapi-bootcamp/
├── api/v1/routes/          # API endpoint definitions
│   ├── user_routes.py
│   └── todo_routes.py
├── controllers/            # Request handlers
├── services/               # Business logic
├── models/                 # SQLAlchemy ORM models
├── schemas/                # Pydantic validation schemas
├── middlewares/            # JWT & RBAC middleware
│   ├── jwt_middleware.py
│   └── role_checker.py
├── db/                     # Database configuration
├── alembic/                # Database migrations
├── tests/                  # Test files
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
└── index.py                # Application entry point
```

---

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback last migration
```bash
alembic downgrade -1
```

---

## Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## Docker Commands

```bash
# Build and start containers
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f app

# Stop containers
docker compose down

# Remove volumes (WARNING: deletes database)
docker compose down -v
```

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: JWT ([python-jose](https://python-jose.readthedocs.io/))
- **Password Hashing**: Argon2
- **Containerization**: Docker & Docker Compose

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - feel free to use this project for learning and production!

---

## Author

**Ali Malim** - [GitHub](https://github.com/alimalim77)
