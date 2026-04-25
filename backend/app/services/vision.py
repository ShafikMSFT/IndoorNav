"""Azure AI Vision service — frame analysis and feature extraction."""

from azure.identity import DefaultAzureCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from app.config import get_settings


def _get_client() -> ImageAnalysisClient:
    settings = get_settings()
    credential = DefaultAzureCredential()
    return ImageAnalysisClient(
        endpoint=settings.azure_vision_endpoint,
        credential=credential,
    )


async def analyze_frame(image_bytes: bytes) -> dict:
    """Analyze a single frame: scene tags, objects, OCR text."""
    client = _get_client()
    result = client.analyze(
        image_data=image_bytes,
        visual_features=[
            VisualFeatures.TAGS,
            VisualFeatures.OBJECTS,
            VisualFeatures.READ,
            VisualFeatures.CAPTION,
        ],
    )
    return {
        "caption": result.caption.text if result.caption else "",
        "tags": [
            {"name": t.name, "confidence": t.confidence}
            for t in (result.tags.list if result.tags else [])
        ],
        "objects": [
            {
                "name": obj.tags[0].name if obj.tags else "unknown",
                "confidence": obj.tags[0].confidence if obj.tags else 0,
                "bounding_box": {
                    "x": obj.bounding_box.x,
                    "y": obj.bounding_box.y,
                    "w": obj.bounding_box.width,
                    "h": obj.bounding_box.height,
                },
            }
            for obj in (result.objects.list if result.objects else [])
        ],
        "ocr_text": [
            line.text
            for block in (result.read.blocks if result.read else [])
            for line in block.lines
        ],
    }


async def get_image_embedding(image_bytes: bytes) -> list[float]:
    """Get a feature vector for visual place recognition.

    Uses Azure AI Vision vectorize-image endpoint.
    """
    import httpx
    from azure.identity import DefaultAzureCredential

    settings = get_settings()
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"{settings.azure_vision_endpoint}/computervision/retrieval:vectorizeImage",
            params={"api-version": "2024-02-01", "model-version": "2023-04-15"},
            headers={
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/octet-stream",
            },
            content=image_bytes,
        )
        resp.raise_for_status()
        return resp.json()["vector"]
