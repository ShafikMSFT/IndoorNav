"""
Azure Function: Frame Extraction

Triggered when a video is uploaded to the 'videos' blob container.
Extracts keyframes using ffmpeg, uploads them to 'frames' container,
and updates Cosmos DB with frame metadata.
"""

import logging
import subprocess
import tempfile
import os
import json

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

app = func.FunctionApp()

DATABASE_NAME = "indoornav"
VIDEOS_CONTAINER = "videos"
FRAMES_CONTAINER = "frames"


def _get_cosmos_database():
    endpoint = os.environ.get("AZURE_COSMOS_ENDPOINT", "")
    if not endpoint:
        raise RuntimeError("AZURE_COSMOS_ENDPOINT not configured")
    client = CosmosClient(url=endpoint, credential=DefaultAzureCredential())
    db = client.create_database_if_not_exists(DATABASE_NAME)
    db.create_container_if_not_exists(
        id=FRAMES_CONTAINER,
        partition_key=PartitionKey(path="/video_id"),
    )
    return db


def _update_video_status(db, video_id: str, status: str, frames_extracted: int = 0, error: str | None = None):
    container = db.get_container_client(VIDEOS_CONTAINER)
    try:
        record = container.read_item(item=video_id, partition_key=video_id)
    except CosmosResourceNotFoundError:
        logging.warning(f"Video record {video_id} not found in Cosmos DB")
        return
    record["status"] = status
    record["frames_extracted"] = frames_extracted
    if error:
        record["error"] = error
    container.upsert_item(record)


@app.blob_trigger(
    arg_name="video_blob",
    path="videos/{name}",
    connection="AzureWebJobsStorage",
)
def extract_frames(video_blob: func.InputStream):
    """Extract keyframes from uploaded video and store in 'frames' container."""
    logging.info(f"Processing video: {video_blob.name}, size: {video_blob.length} bytes")

    # video_blob.name is "videos/{video_id}/{filename}"
    # Extract video_id from the path
    blob_path = video_blob.name or ""
    parts = blob_path.replace("videos/", "", 1).split("/", 1)
    video_id = parts[0] if parts else "unknown"

    credential = DefaultAzureCredential()
    blob_endpoint = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT", "")
    blob_service = BlobServiceClient(account_url=blob_endpoint, credential=credential)

    # Update status to processing
    db = None
    try:
        db = _get_cosmos_database()
        _update_video_status(db, video_id, "processing")
    except Exception as e:
        logging.warning(f"Could not update Cosmos status: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save video to temp file
        video_path = os.path.join(tmpdir, "input_video.mp4")
        with open(video_path, "wb") as f:
            f.write(video_blob.read())

        # Extract keyframes with ffmpeg (1 frame per second)
        output_pattern = os.path.join(tmpdir, "frame_%06d.jpg")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fps=1,select='eq(pict_type\\,I)'",
            "-vsync", "vfr",
            "-q:v", "2",
            output_pattern,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback: extract at 1fps without keyframe filter
            cmd_fallback = [
                "ffmpeg", "-i", video_path,
                "-vf", "fps=1",
                "-q:v", "2",
                output_pattern,
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True, timeout=600)

        # Upload extracted frames
        frames = sorted(
            f for f in os.listdir(tmpdir) if f.startswith("frame_") and f.endswith(".jpg")
        )

        logging.info(f"Extracted {len(frames)} frames for video {video_id}")

        # Ensure frames container exists
        try:
            blob_service.create_container("frames")
        except Exception:
            pass  # Already exists

        frames_container = blob_service.get_container_client("frames")
        frame_metadata = []

        for i, frame_file in enumerate(frames):
            frame_path = os.path.join(tmpdir, frame_file)
            blob_name = f"{video_id}/frame_{i:06d}.jpg"

            with open(frame_path, "rb") as f:
                frames_container.upload_blob(name=blob_name, data=f, overwrite=True)

            frame_metadata.append({
                "frame_index": i,
                "blob_name": blob_name,
                "timestamp_sec": i,  # 1fps → frame index ≈ seconds
            })

        # Write frame records to Cosmos DB
        if db:
            try:
                frames_cosmos = db.get_container_client(FRAMES_CONTAINER)
                for frame in frame_metadata:
                    record = {
                        "id": f"{video_id}_frame_{frame['frame_index']:06d}",
                        "video_id": video_id,
                        "frame_index": frame["frame_index"],
                        "blob_name": frame["blob_name"],
                        "timestamp_sec": frame["timestamp_sec"],
                    }
                    frames_cosmos.upsert_item(record)

                _update_video_status(db, video_id, "completed", frames_extracted=len(frames))
                logging.info(f"Updated Cosmos DB: {len(frames)} frames for video {video_id}")
            except Exception as e:
                logging.error(f"Failed to write frame records to Cosmos: {e}")
                _update_video_status(db, video_id, "failed", error=str(e))
        else:
            # Fallback: store extraction result in blob
            maps_container = blob_service.get_container_client("maps")
            try:
                blob_service.create_container("maps")
            except Exception:
                pass
            metadata_blob = maps_container.get_blob_client(f"{video_id}/extraction_result.json")
            metadata_blob.upload_blob(
                json.dumps({
                    "video_id": video_id,
                    "source_video": video_blob.name,
                    "frame_count": len(frames),
                    "frames": frame_metadata,
                    "status": "frames_extracted",
                }),
                overwrite=True,
            )

        logging.info(f"Frame extraction complete for video {video_id}: {len(frames)} frames")
