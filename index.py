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
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from middlewares.jwt_middleware import JWTAuthMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(bind=engine) # DISABLED: Using Alembic migrations
    yield

app = FastAPI(
    title="FastAPI Clean Architecture",
    lifespan=lifespan  
)

app.add_middleware(JWTAuthMiddleware)

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(todo_router, prefix="/api/v1/todos", tags=["Todos"])
app.include_router(board_router, prefix="/api/v1/boards", tags=["Boards"])

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc):
    errors = [{"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})       