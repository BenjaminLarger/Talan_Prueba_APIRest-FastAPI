from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


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
        from datetime import datetime
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
        from datetime import datetime
        datetime.strptime(v, "%d/%m/%Y")
        return v


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}
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
        from datetime import datetime
        if isinstance(v, str):
            return datetime.strptime(v, "%d/%m/%Y").date()
        return v


class PaginatedTaskResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    size: int
    pages: int
