from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)