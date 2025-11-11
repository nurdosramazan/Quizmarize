from fastapi_users import schemas
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class UserRead(schemas.BaseUser[int]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class TaskRead(BaseModel):
    id: int
    task_type: str
    task_data: Dict[str, Any]

    class Config:
        from_attributes = True

class SummaryRead(BaseModel):
    id: int
    summary_text: str
    tasks: List[TaskRead] = []

    class Config:
        from_attributes = True

class FileRead(BaseModel):
    id: int
    filename: str
    content_type: str
    uploaded_at: Any
    status: str

    class Config:
        from_attributes = True

class FileDetailRead(FileRead):
    summary: Optional[SummaryRead] = None

    class Config:
        from_attributes = True
