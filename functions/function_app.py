"""
Azure Function: Frame Extraction

Triggered when a video is uploaded to the 'videos' blob container.
Extracts keyframes using ffmpeg, uploads them to 'frames' container,
and queues AI Vision analysis for each frame.
"""

import logging
import subprocess
import tempfile
import os
import uuid
import json

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()


@app.blob_trigger(
    arg_name="video_blob",
    path="videos/{name}",
    connection="AzureWebJobsStorage",
)
def extract_frames(video_blob: func.InputStream):
    """Extract keyframes from uploaded video and store in 'frames' container."""
    logging.info(f"Processing video: {video_blob.name}, size: {video_blob.length} bytes")

    map_id = str(uuid.uuid4())
    credential = DefaultAzureCredential()

    blob_endpoint = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT", "")
    blob_service = BlobServiceClient(account_url=blob_endpoint, credential=credential)

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
        except FileNotFoundError:
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

        logging.info(f"Extracted {len(frames)} frames for map {map_id}")

        frames_container = blob_service.get_container_client("frames")
        frame_metadata = []

        for i, frame_file in enumerate(frames):
            frame_path = os.path.join(tmpdir, frame_file)
            blob_name = f"{map_id}/frame_{i:06d}.jpg"

            with open(frame_path, "rb") as f:
                frames_container.upload_blob(name=blob_name, data=f, overwrite=True)

            frame_metadata.append({
                "frame_index": i,
                "blob_name": blob_name,
                "map_id": map_id,
            })

        # Store processing metadata
        maps_container = blob_service.get_container_client("maps")
        metadata_blob = maps_container.get_blob_client(f"{map_id}/extraction_result.json")
        metadata_blob.upload_blob(
            json.dumps({
                "map_id": map_id,
                "source_video": video_blob.name,
                "frame_count": len(frames),
                "frames": frame_metadata,
                "status": "frames_extracted",
            }),
            overwrite=True,
        )

        logging.info(f"Frame extraction complete for map {map_id}: {len(frames)} frames")
