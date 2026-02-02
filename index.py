from dotenv import load_dotenv
load_dotenv()  # Load .env file

import os
print(f"[DEBUG] EMAIL_ADDRESS: {os.getenv('EMAIL_ADDRESS')}")
print(f"[DEBUG] EMAIL_PASSWORD: {os.getenv('EMAIL_PASSWORD')}")

from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import engine, Base
from models import User
from api.v1.routes.user_routes import router as user_router
from api.v1.routes.todo_routes import router as todo_router
from api.v1.routes.board_routes import router as board_router
from api.v1.routes.list_routes import router as list_router
from api.v1.routes.label_routes import router as label_router
from api.v1.routes.card_routes import router as card_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from middlewares.jwt_middleware import JWTAuthMiddleware
from prometheus_client import make_asgi_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(bind=engine) # DISABLED: Using Alembic migrations
    yield

app = FastAPI(
    title="FastAPI Clean Architecture",
    lifespan=lifespan  
)

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

app.add_middleware(JWTAuthMiddleware)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(todo_router, prefix="/api/v1/todos", tags=["Todos"])
app.include_router(board_router, prefix="/api/v1/boards", tags=["Boards"])
app.include_router(list_router, prefix="/api/v1", tags=["Lists"])
app.include_router(label_router, prefix="/api/v1", tags=["Labels"])
app.include_router(card_router, prefix="/api/v1", tags=["Cards"])

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc):
    errors = [{"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})       
       