from app.database import Base
from sqlalchemy import Column, Date, Enum, Integer, String

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    hashed_password = Column(String)


