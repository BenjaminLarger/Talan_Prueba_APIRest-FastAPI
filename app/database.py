from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create SQLite engine
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "done"


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# Databasee Model
class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(String(100))
    status = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)


# Link our engine with our table
Base.metadata.create_all(engine)


# Pydantic Models (Dataclass)
class TaskCreate(BaseModel):
    title: str
    description: str
    status: StatusEnum
    priority: PriorityEnum
    due_date: Optional[str] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return None
        datetime.strptime(v, "%d/%m/%Y")
        return v


# Response model for returning task data to protect any private information
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: StatusEnum
    priority: PriorityEnum
    due_date: Optional[str] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def convert_due_date(cls, v):
        if isinstance(v, date):
            return v.strftime("%d/%m/%Y")
        return v

    class Config:
        from_attributes = True


def get_db():
    """Dependency to get a database session"""
    db = SessionLocal()
    try:
        yield db  # We try to create the database and yield it to the caller
    finally:
        db.close()
