"""Cosmos DB SQL API service — video/frame metadata storage."""

import logging
from datetime import datetime, timezone

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

from app.config import get_settings

logger = logging.getLogger(__name__)

_client = None
_database = None

DATABASE_NAME = "indoornav"
VIDEOS_CONTAINER = "videos"
FRAMES_CONTAINER = "frames"


def _get_database():
    global _client, _database
    if _database is not None:
        return _database

    settings = get_settings()
    endpoint = settings.azure_cosmos_endpoint
    if not endpoint:
        raise RuntimeError("AZURE_COSMOS_ENDPOINT not configured")

    _client = CosmosClient(url=endpoint, credential=DefaultAzureCredential())
    _database = _client.create_database_if_not_exists(DATABASE_NAME)

    # Ensure containers exist
    _database.create_container_if_not_exists(
        id=VIDEOS_CONTAINER,
        partition_key=PartitionKey(path="/id"),
    )
    _database.create_container_if_not_exists(
        id=FRAMES_CONTAINER,
        partition_key=PartitionKey(path="/video_id"),
    )
    return _database


async def create_video_record(
    video_id: str,
    blob_name: str,
    blob_url: str,
    original_filename: str,
    size_bytes: int,
) -> dict:
    """Create a video metadata record."""
    db = _get_database()
    container = db.get_container_client(VIDEOS_CONTAINER)
    record = {
        "id": video_id,
        "blob_name": blob_name,
        "blob_url": blob_url,
        "original_filename": original_filename,
        "size_bytes": size_bytes,
        "status": "uploaded",
        "frames_extracted": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    container.upsert_item(record)
    logger.info(f"Created video record {video_id}")
    return record


async def get_video_record(video_id: str) -> dict | None:
    """Get a video metadata record by ID."""
    db = _get_database()
    container = db.get_container_client(VIDEOS_CONTAINER)
    try:
        return container.read_item(item=video_id, partition_key=video_id)
    except CosmosResourceNotFoundError:
        return None


async def update_video_status(
    video_id: str, status: str, frames_extracted: int = 0, error: str | None = None
) -> dict | None:
    """Update video processing status."""
    record = await get_video_record(video_id)
    if not record:
        return None
    record["status"] = status
    record["frames_extracted"] = frames_extracted
    if error:
        record["error"] = error
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    db = _get_database()
    container = db.get_container_client(VIDEOS_CONTAINER)
    container.upsert_item(record)
    return record


async def create_frame_records(video_id: str, frames: list[dict]) -> None:
    """Batch-create frame metadata records."""
    db = _get_database()
    container = db.get_container_client(FRAMES_CONTAINER)
    for frame in frames:
        record = {
            "id": f"{video_id}_frame_{frame['frame_index']:06d}",
            "video_id": video_id,
            "frame_index": frame["frame_index"],
            "blob_name": frame["blob_name"],
            "timestamp_sec": frame.get("timestamp_sec", frame["frame_index"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        container.upsert_item(record)
    logger.info(f"Created {len(frames)} frame records for video {video_id}")


async def get_frames_for_video(video_id: str) -> list[dict]:
    """Get all frame records for a video."""
    db = _get_database()
    container = db.get_container_client(FRAMES_CONTAINER)
    query = "SELECT * FROM c WHERE c.video_id = @vid ORDER BY c.frame_index"
    items = list(
        container.query_items(
            query=query,
            parameters=[{"name": "@vid", "value": video_id}],
            enable_cross_partition_query=True,
        )
    )
    return items
