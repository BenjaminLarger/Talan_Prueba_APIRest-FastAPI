from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, tasks
from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
