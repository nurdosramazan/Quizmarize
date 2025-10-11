import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import current_active_user
from ..database import get_async_session
from ..models import User, File as DBFile

router = APIRouter()

# Define the base directory for uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload/", tags=["Uploads"])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Upload a file and save it to the server.
    Creates a corresponding record in the database.
    """
    if not file.content_type:
        raise HTTPException(status_code=400, detail="File has no content type")

    # Define the path where the file will be saved
    file_location = UPLOAD_DIR / f"{user.id}_{file.filename}"

    # Save the file to the local directory
    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Create a database record for the file
    db_file = DBFile(
        filename=file.filename,
        file_path=str(file_location),
        content_type=file.content_type,
        owner_id=user.id
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "content_type": db_file.content_type,
        "file_path": db_file.file_path,
    }