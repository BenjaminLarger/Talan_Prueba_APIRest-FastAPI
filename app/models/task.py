from sqlalchemy import Column, Date, ForeignKey, Integer, String

from app.database import Base


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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
