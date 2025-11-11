import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


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
    summary = relationship("Summary", back_populates="file", uselist=False)

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    file_id = Column(Integer, ForeignKey("files.id"))
    file = relationship("File", back_populates="summary")

    tasks = relationship("Task", back_populates="summary")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, nullable=False)  # e.g., "multiple_choice", "open_question"

    # JSONB is perfect for storing flexible data like questions, options, and answers
    task_data = Column(JSONB, nullable=False)

    summary_id = Column(Integer, ForeignKey("summaries.id"))
    summary = relationship("Summary", back_populates="tasks")