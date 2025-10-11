import uuid
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import current_active_user
from ..database import get_async_session
from ..models import User, File as DBFile
from ..storage import storage_service

router = APIRouter()

@router.post("/upload/", tags=["Uploads"])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Upload a file to cloud storage.
    Creates a corresponding record in the database.
    """
    if not file.content_type:
        raise HTTPException(status_code=400, detail="File has no content type")

    # Generate a unique filename to avoid collisions
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    object_name = f"user_{user.id}/{uuid.uuid4()}.{file_extension}"

    # Use the storage service to upload the file
    file_url = storage_service.upload_file(
        file_object=file.file,
        object_name=object_name,
        content_type=file.content_type
    )

    if not file_url:
        raise HTTPException(status_code=500, detail="Could not upload file.")

    # Create a database record for the file
    db_file = DBFile(
        filename=file.filename,
        # The file_path is now the S3 object key or URL
        file_path=object_name,
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
        "file_url": file_url,
    }