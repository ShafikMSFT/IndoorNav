"""POI (Point of Interest) management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import require_admin, get_current_user

router = APIRouter()


class POI(BaseModel):
    poi_id: str
    map_id: str
    name: str
    description: str
    node_id: str
    category: str


class POICreate(BaseModel):
    map_id: str
    name: str
    description: str
    node_id: str
    category: str = "general"


@router.get("/{map_id}", response_model=list[POI])
async def list_pois(map_id: str):
    """List all POIs for a map."""
    # TODO: Query Cosmos DB
    return []


@router.post("/", response_model=POI)
async def create_poi(poi: POICreate, _user: dict = Depends(require_admin)):
    """Create a new POI on a map node."""
    # TODO: Save to Cosmos DB + generate embedding via Azure OpenAI
    return POI(poi_id="placeholder", **poi.model_dump())


@router.post("/{map_id}/search")
async def search_pois(map_id: str, query: str):
    """Search POIs using natural language via Azure OpenAI + AI Search."""
    # TODO: Embed query → vector search AI Search index → return matches
    return {"query": query, "results": []}
