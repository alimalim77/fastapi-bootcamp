from fastapi import FastAPI
from contextlib import asynccontextmanager
from ticketing_system.db.database import engine, Base
from ticketing_system.models import User
from ticketing_system.api.v1.routes.user_routes import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="FastAPI Clean Architecture",
    lifespan=lifespan  
)

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
