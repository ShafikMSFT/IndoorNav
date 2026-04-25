"""Blob Storage service — upload/download videos and frames."""

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from app.config import get_settings


def _get_client() -> BlobServiceClient:
    settings = get_settings()
    credential = DefaultAzureCredential()
    return BlobServiceClient(
        account_url=settings.azure_storage_blob_endpoint,
        credential=credential,
    )


async def upload_video(video_bytes: bytes, filename: str) -> str:
    """Upload video to the 'videos' container. Returns blob URL."""
    client = _get_client()
    blob_client = client.get_blob_client(container="videos", blob=filename)
    blob_client.upload_blob(video_bytes, overwrite=True)
    return blob_client.url


async def upload_frame(frame_bytes: bytes, map_id: str, frame_index: int) -> str:
    """Upload an extracted frame to the 'frames' container."""
    client = _get_client()
    blob_name = f"{map_id}/frame_{frame_index:06d}.jpg"
    blob_client = client.get_blob_client(container="frames", blob=blob_name)
    blob_client.upload_blob(frame_bytes, overwrite=True)
    return blob_client.url


async def get_frame_url(map_id: str, frame_index: int) -> str:
    """Get the URL for a stored frame."""
    settings = get_settings()
    return f"{settings.azure_storage_blob_endpoint}frames/{map_id}/frame_{frame_index:06d}.jpg"
