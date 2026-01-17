from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import engine, Base
from models import User
from api.v1.routes.user_routes import router as user_router
from api.v1.routes.todo_routes import router as todo_router
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

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc):
    return JSONResponse(...)       