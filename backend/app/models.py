import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
from fastapi_users.db import SQLAlchemyBaseUserTable


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    # This creates a one-to-many relationship: one user can have many files
    files = relationship("File", back_populates="owner")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    content_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    status = Column(String, default="uploaded")  # e.g., uploaded, processing, completed, failed
    content = Column(Text, nullable=True)  # To store the extracted text

    # Foreign key to link to the 'users' table
    owner_id = Column(Integer, ForeignKey("user.id"))

    # This creates the other side of the relationship
    owner = relationship("User", back_populates="files")