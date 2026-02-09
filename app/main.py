from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.config import settings
from app.database import (Base, PaginatedTaskResponse, PriorityEnum,
                          StatusEnum, TaskCreate, TaskFilter, TaskOrder,
                          TaskPartialUpdate, TaskResponse, Tasks, engine,
                          get_db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/all_tasks/", response_model=list[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Tasks).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/", response_model=PaginatedTaskResponse)
def list_tasks(
    page: int = 1,
    size: int = 10,
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
    sort_by: TaskFilter = TaskFilter.created_at,
    order: TaskOrder = TaskOrder.asc,
    db: Session = Depends(get_db),
):
    query_set = db.query(Tasks)

    if status:
        query_set = query_set.filter(Tasks.status == status.value)
    if priority:
        query_set = query_set.filter(Tasks.priority == priority.value)

    # Parse date filters
    if due_before:
        due_before_date = datetime.strptime(due_before, "%d/%m/%Y").date()
        query_set = query_set.filter(Tasks.due_date < due_before_date)
    if due_after:
        due_after_date = datetime.strptime(due_after, "%d/%m/%Y").date()
        query_set = query_set.filter(Tasks.due_date > due_after_date)

    sort_column = getattr(Tasks, sort_by.value)
    order_func = asc if order == TaskOrder.asc else desc
    query_set = query_set.order_by(order_func(sort_column))

    total = query_set.count()
    items = query_set.offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return PaginatedTaskResponse(
        items=items, total=total, page=page, size=size, pages=pages
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    user = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Task not found")
    return user


@app.post("/tasks/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    # Convert due_date from DD/MM/YYYY string to date object
    due_date_obj = None
    if task.due_date:
        due_date_obj = datetime.strptime(task.due_date, "%d/%m/%Y").date()
    current_date = date.today()

    # Create a new task instance
    new_task = Tasks(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=due_date_obj,
        created_at=current_date,
        updated_at=current_date,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    existing_task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Convert due_date from DD/MM/YYYY string to date object
    due_date_obj = None
    if task.due_date:
        due_date_obj = datetime.strptime(task.due_date, "%d/%m/%Y").date()

    existing_task.title = task.title
    existing_task.description = task.description
    existing_task.status = task.status
    existing_task.priority = task.priority
    existing_task.due_date = due_date_obj
    existing_task.updated_at = date.today()

    db.commit()
    db.refresh(existing_task)
    return existing_task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task_partial(
    task_id: int, task: TaskPartialUpdate, db: Session = Depends(get_db)
):
    existing_task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.title is not None:
        existing_task.title = task.title
    if task.description is not None:
        existing_task.description = task.description
    if task.status is not None:
        existing_task.status = task.status
    if task.priority is not None:
        existing_task.priority = task.priority
    if task.due_date is not None:
        existing_task.due_date = datetime.strptime(task.due_date, "%d/%m/%Y").date()

    existing_task.updated_at = date.today()

    db.commit()
    db.refresh(existing_task)
    return existing_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    existing_task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(existing_task)
    db.commit()
    return {}


@app.delete("/tasks/", status_code=204)
def delete_all_tasks(db: Session = Depends(get_db)):
    db.query(Tasks).delete()
    db.commit()
    return {}
