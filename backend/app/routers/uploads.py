import uuid
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import current_active_user
from ..database import get_async_session
from ..models import User, File as DBFile
from ..storage import storage_service
from ..parsers import parse_content

router = APIRouter()

@router.post("/upload/", tags=["Uploads"])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    1. Upload a file to cloud storage.
    2. Create a database record.
    3. Retrieve the file and parse its text content.
    4. Update the database record with the extracted text.
    """
    # --- Step 1 & 2: Upload and create initial DB record (mostly unchanged) ---
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
        file_path=object_name,
        content_type=file.content_type,
        owner_id=user.id,
        status="uploaded"
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    # --- Step 3: Download from storage and parse ---
    db_file.status = "processing"
    await db.commit()

    file_buffer = storage_service.download_file(object_name)
    if not file_buffer:
        db_file.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail="Could not retrieve file for processing.")

    extracted_content = parse_content(file_buffer, db_file.content_type)

    # --- Step 4: Update DB record with content and final status ---
    db_file.content = extracted_content
    db_file.status = "completed"

    await db.commit()
    await db.refresh(db_file)

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "content_type": db_file.content_type,
        "file_url": file_url,
        "status": db_file.status,
        "content_preview": (extracted_content or "")[:200] + "..."
    }