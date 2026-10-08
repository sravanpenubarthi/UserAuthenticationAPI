"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registers models with Base)
from app.config import APP_TITLE, APP_VERSION
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="User registration and login API with bcrypt password hashing (Day 8).",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "User Authentication API is running"}
