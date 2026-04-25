"""Map management endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MapSummary(BaseModel):
    map_id: str
    name: str
    node_count: int
    poi_count: int
    status: str


@router.get("/", response_model=list[MapSummary])
async def list_maps():
    """List all available maps."""
    # TODO: Query Cosmos DB for maps
    return []


@router.get("/{map_id}")
async def get_map(map_id: str):
    """Get full map graph data (nodes + edges) for rendering."""
    # TODO: Query Gremlin graph for map_id
    return {"map_id": map_id, "nodes": [], "edges": []}


@router.get("/{map_id}/graph")
async def get_map_graph(map_id: str):
    """Get the spatial graph for pathfinding visualization."""
    # TODO: Return graph structure from Cosmos Gremlin
    return {"map_id": map_id, "nodes": [], "edges": []}
