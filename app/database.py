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


class TaskFilter(str, Enum):
    created_at = "created_at"
    due_date = "due_date"
    priority = "priority"
    status = "status"


class TaskOrder(str, Enum):
    asc = "asc"
    desc = "desc"


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


class TaskPartialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
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


class TaskQueryParams(BaseModel):
    page: int = 1
    size: int = 10
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_before: Optional[str] = None
    due_after: Optional[str] = None
    sort_by: Optional[TaskFilter] = TaskFilter.created_at
    order: Optional[TaskOrder] = TaskOrder.asc

    @field_validator(
        "due_before",
        "due_after",
    )
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y").date()
        return v


class PaginatedTaskResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    size: int
    pages: int


def get_db():
    """Dependency to get a database session"""
    db = SessionLocal()
    try:
        yield db  # We try to create the database and yield it to the caller
    finally:
        db.close()
