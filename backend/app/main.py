from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import maps, navigation, videos, pois

settings = get_settings()

app = FastAPI(
    title="Indoor Navigation API",
    version="0.1.0",
    description="API for indoor video-to-map navigation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(maps.router, prefix="/api/maps", tags=["maps"])
app.include_router(pois.router, prefix="/api/pois", tags=["pois"])
app.include_router(navigation.router, prefix="/api/navigation", tags=["navigation"])


@app.get("/health")
async def health():
    return {"status": "ok"}
