
# Azure Services Map

## Core Services

| Concern | Azure Service | Resource Name | Status |
|---|---|---|---|
| Video/frame analysis & feature extraction | **Azure AI Vision 4.0** (Image Analysis, Spatial Analysis) | `indoornav-dev-vision` | ✅ Deployed |
| Natural language destination + orchestration | **Azure OpenAI GPT-4o** via Azure AI Foundry | `indoornav-dev-openai` | ✅ Deployed |
| Embedding-based POI matching | **Azure OpenAI Embeddings** (text-embedding-3-small) | `indoornav-dev-openai` | ✅ Deployed |
| Video & frame storage | **Azure Blob Storage** | `indoornavdevstor` | ✅ Deployed |
| Spatial graph (pathfinding) | **Azure Cosmos DB** — Gremlin API | `indoornav-dev-cosmos` | ✅ Deployed |
| Metadata (maps, frames, POIs) | **Azure Cosmos DB** — SQL API | `indoornav-dev-cosmos-sql` | ✅ Deployed |
| POI semantic search | **Azure AI Search** | `indoornav-dev-search` | ✅ Deployed |
| Backend API | **Azure App Service** (Python 3.11 / FastAPI) | `indoornav-dev-api` | ✅ Deployed |
| Video processing pipeline | **Azure Functions** (Blob-triggered, Python) | `indoornav-dev-functions` | ✅ Deployed |
| Real-time navigation updates | **Azure SignalR Service** | `indoornav-dev-signalr` | ✅ Deployed |
| Monitoring & telemetry | **Azure Application Insights** + Log Analytics | `indoornav-dev-insights` | ✅ Deployed |

## Planned (Not Yet Provisioned)

| Concern | Azure Service | Notes |
|---|---|---|
| Auth | **Microsoft Entra ID** (MSAL) | Admin vs. User roles |
| Indoor map tiles (optional) | **Azure Maps — Indoor Maps** | If we need 2D floor plan rendering |

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     ADMIN FLOW                           │
│                                                          │
│  Upload Video ──► Blob Storage ──► Azure Function        │
│                                    (frame extraction)    │
│                                         │                │
│                          ┌──────────────┘                │
│                          ▼                               │
│                   Azure AI Vision                        │
│                   • Scene/object detection               │
│                   • OCR (room signs, labels)             │
│                   • Feature vectors per frame            │
│                          │                               │
│                          ▼                               │
│              Map Builder Service                         │
│              • Stitch frames into spatial graph          │
│              • Auto-detect POIs (doors, signs, desks)    │
│              • Admin reviews & labels POIs               │
│                          │                               │
│                          ▼                               │
│              Cosmos DB (Graph + SQL)                     │
│              • Nodes = locations/frames                  │
│              • Edges = navigable connections             │
│              • POI metadata + embeddings                 │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                     USER FLOW                            │
│                                                          │
│  1. Open camera ──► capture frame ──► Azure AI Vision    │
│     (or select POI manually)    feature vector match     │
│                                         │                │
│                          ┌──────────────┘                │
│                          ▼                               │
│            Localization: match to nearest graph node     │
│            ══► POINT A established                       │
│                                                          │
│  2. Describe destination in natural language             │
│     (or select POI manually)                             │
│                          │                               │
│                          ▼                               │
│         Azure OpenAI GPT-4o                              │
│         • Parse intent ("take me to the kitchen")        │
│         • Embedding similarity → match POI               │
│         ══► POINT B established                          │
│                                                          │
│  3. Pathfinding (Cosmos Gremlin / A*)                    │
│         A ──► shortest path ──► B                        │
│                          │                               │
│  4. Turn-by-turn guidance via camera                     │
│     • Continuous frame capture → re-localize             │
│     • AR overlay arrows / text instructions              │
│     • SignalR for real-time updates                      │
└──────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite, Three.js/WebGL for AR overlay |
| Backend API | Python FastAPI on Azure App Service |
| Video Processing | Azure Functions (Python) + FFmpeg |
| Graph Database | Azure Cosmos DB (Gremlin API) |
| Metadata Database | Azure Cosmos DB (SQL API) |
| AI Vision | Azure AI Vision 4.0 (analysis + image embeddings) |
| LLM | Azure OpenAI GPT-4o (via AI Foundry) |
| Search | Azure AI Search (vector + hybrid) |
| Real-time | Azure SignalR Service |
| Storage | Azure Blob Storage |
| IaC | Bicep templates |
| Region | Sweden Central |
