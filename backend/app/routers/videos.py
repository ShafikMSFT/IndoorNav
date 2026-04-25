"""Video upload and management endpoints."""

import uuid
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from app.auth import require_admin
from app.services.storage import upload_video
from app.services.cosmos import create_video_record, get_video_record

logger = logging.getLogger(__name__)

router = APIRouter()


class VideoUploadResponse(BaseModel):
    video_id: str
    blob_url: str
    status: str


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video_endpoint(
    file: UploadFile = File(...), _user: dict = Depends(require_admin)
):
    """Upload a walkthrough video for processing."""
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    video_id = str(uuid.uuid4())
    original_name = file.filename or "video.mp4"
    blob_name = f"{video_id}/{original_name}"

    # Read file and upload to Blob Storage
    video_bytes = await file.read()
    if len(video_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    logger.info(f"Uploading video {video_id} ({len(video_bytes)} bytes)")
    blob_url = await upload_video(video_bytes, blob_name)

    # Create metadata record in Cosmos DB
    await create_video_record(
        video_id=video_id,
        blob_name=blob_name,
        blob_url=blob_url,
        original_filename=original_name,
        size_bytes=len(video_bytes),
    )

    return VideoUploadResponse(
        video_id=video_id,
        blob_url=blob_url,
        status="uploaded",
    )


@router.get("/{video_id}/status")
async def get_processing_status(video_id: str):
    """Check video processing status."""
    record = await get_video_record(video_id)
    if not record:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "video_id": record["id"],
        "status": record.get("status", "unknown"),
        "frames_extracted": record.get("frames_extracted", 0),
        "error": record.get("error"),
    }
