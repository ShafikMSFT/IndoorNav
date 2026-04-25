"""Video upload and management endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from app.auth import require_admin

router = APIRouter()


class VideoUploadResponse(BaseModel):
    video_id: str
    blob_url: str
    status: str


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...), _user: dict = Depends(require_admin)):
    """Upload a walkthrough video for processing."""
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # TODO: Upload to Azure Blob Storage, trigger frame extraction
    return VideoUploadResponse(
        video_id="placeholder",
        blob_url="",
        status="queued",
    )


@router.get("/{video_id}/status")
async def get_processing_status(video_id: str):
    """Check video processing status."""
    # TODO: Query Cosmos DB for processing state
    return {"video_id": video_id, "status": "pending", "frames_extracted": 0}
