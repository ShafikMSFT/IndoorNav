"""Navigation endpoints — localization, destination resolution, pathfinding."""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter()


class LocalizationResult(BaseModel):
    node_id: str
    confidence: float
    label: str


class NavigationRequest(BaseModel):
    map_id: str
    start_node_id: str
    destination_text: str | None = None
    destination_node_id: str | None = None


class NavigationStep(BaseModel):
    node_id: str
    instruction: str
    frame_url: str | None = None


class NavigationRoute(BaseModel):
    start_node_id: str
    end_node_id: str
    steps: list[NavigationStep]
    total_nodes: int


@router.post("/{map_id}/localize", response_model=LocalizationResult)
async def localize(map_id: str, frame: UploadFile = File(...)):
    """
    Accept a camera frame, extract features via Azure AI Vision,
    and match against the map's spatial graph to determine current location.
    """
    # TODO:
    # 1. Send frame to Azure AI Vision → get feature vector
    # 2. Compare against stored node vectors (nearest neighbor)
    # 3. Return best-match node
    return LocalizationResult(node_id="", confidence=0.0, label="unknown")


@router.post("/{map_id}/resolve-destination")
async def resolve_destination(map_id: str, query: str):
    """
    Use Azure OpenAI to parse a natural-language destination description
    and match it to a POI via embedding similarity (AI Search).
    """
    # TODO:
    # 1. GPT-4o function-calling to extract destination entity
    # 2. Embed entity → vector search POIs
    # 3. Return matched POI(s) with confidence
    return {"query": query, "matched_pois": []}


@router.post("/{map_id}/route", response_model=NavigationRoute)
async def compute_route(request: NavigationRequest):
    """
    Compute shortest path from start to destination node.
    Optionally generate natural-language turn-by-turn directions via GPT-4o.
    """
    # TODO:
    # 1. If destination_text given, resolve to node via resolve_destination
    # 2. Run A* / Gremlin shortest path
    # 3. Generate human-friendly step instructions via Azure OpenAI
    return NavigationRoute(
        start_node_id=request.start_node_id,
        end_node_id=request.destination_node_id or "",
        steps=[],
        total_nodes=0,
    )
