from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from typing import List

from ..auth import current_active_user
from ..database import get_async_session
from ..models import User, File as DBFile
from ..schemas import FileRead, FileDetailRead

router = APIRouter()


@router.get("/files/", tags=["Content"], response_model=List[FileRead])
async def get_user_files(
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    query = select(DBFile).where(DBFile.owner_id == user.id).order_by(DBFile.uploaded_at.desc())
    result = await db.execute(query)
    files = result.scalars().all()
    return files


@router.get("/files/{file_id}", tags=["Content"], response_model=FileDetailRead)
async def get_file_details(
        file_id: int,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    # This is "eager loading": We load the file AND its related summary
    # AND the summary's related tasks all in one query.
    query = (
        select(DBFile)
        .where(DBFile.id == file_id)
        .options(
            selectinload(DBFile.summary).selectinload(DBFile.summary.property.mapper.class_.tasks)
        )

    )
    result = await db.execute(query)
    file = result.scalars().first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Security check:
    if file.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    return file
