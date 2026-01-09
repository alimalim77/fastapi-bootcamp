from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import engine, Base
from models import User
from api.v1.routes.user_routes import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="FastAPI Clean Architecture",
    lifespan=lifespan  
)

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
