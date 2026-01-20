# Configuration

Environment variables, Docker setup, and deployment.

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DATABASE_URL` | `sqlite:///./app.db` | No | Database connection string |
| `SECRET_KEY` | `supersecretkey` | **Yes** (production) | JWT signing key |
| `EMAIL_ADDRESS` | - | **Yes** | Gmail address for OTP emails |
| `EMAIL_PASSWORD` | - | **Yes** | Gmail App Password (16-char) |

### .env Example

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-super-secret-key-change-in-production
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Production Recommendations

| Variable | Recommendation |
|----------|----------------|
| `SECRET_KEY` | Use 32+ character random string |
| `DATABASE_URL` | Use PostgreSQL in production |
| `EMAIL_PASSWORD` | Use Gmail App Password, not regular password |

---

## Running the Application

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn index:app --reload
```

### Production

```bash
# Without Docker
uvicorn index:app --host 0.0.0.0 --port 8000

# With Docker
docker-compose up
```

---

## Database Migrations

### Creating Migrations

```bash
# After modifying models, generate migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View current version
alembic current
```

### Common Migration Commands

```bash
# Reset database (development only)
alembic downgrade base
alembic upgrade head

# View migration history
alembic history
```

---

## Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - SECRET_KEY=${SECRET_KEY}
      - EMAIL_ADDRESS=${EMAIL_ADDRESS}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    volumes:
      - ./app.db:/app/app.db
```

### Docker Commands

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## Gmail App Password Setup

Required for OTP email functionality.

1. **Enable 2-Factor Authentication**
   - Go to [Google Account](https://myaccount.google.com)
   - Security → 2-Step Verification → Turn on

2. **Generate App Password**
   - Security → App Passwords
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password

3. **Configure Environment**
   ```env
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## API Documentation

After starting the server, access:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc (alternative docs) |
| `http://localhost:8000/openapi.json` | OpenAPI spec (JSON) |

---

## Future Enhancements

Consider adding these features:

- **Rate Limiting**: Protect against brute force attacks
- **Password Reset**: Using OTP infrastructure
- **OAuth2 Social Login**: Google, GitHub integration
- **API Versioning Strategy**: Support multiple API versions
- **Caching Layer**: Redis for session and response caching
- **Background Tasks**: Celery for async operations
- **Monitoring**: Prometheus metrics and health endpoints
- **Logging**: Structured logging with correlation IDs

---

[← Back to Index](./README.md) | [Previous: Testing](./13-testing.md)
