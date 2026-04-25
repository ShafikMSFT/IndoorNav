# Indoor Navigation — Full Backlog

## Sprint Plan

| Sprint | Epics | Deliverable |
|---|---|---|
| **Sprint 1** | 1 + 2 | Infra provisioned; admin can upload video; frames extracted |
| **Sprint 2** | 3 + 4 | Frames analyzed by AI; spatial graph built; admin editor |
| **Sprint 3** | 5 + 6 | User can localize via camera; destination via natural language |
| **Sprint 4** | 7 + 8 | Full navigation loop: A → B with camera guidance |
| **Sprint 5** | 9 | Production hardening, PWA, analytics |

---

## Epic 1 — Project Scaffolding & Azure Infrastructure

| # | Story | Status |
|---|---|---|
| 1.1 | Set up monorepo (React Vite frontend + Python FastAPI backend + Azure Functions) | ✅ Done |
| 1.2 | Provision Azure resources via Bicep (Blob, Cosmos, AI Vision, OpenAI, Functions, App Service, SignalR, AI Search, Monitoring) | ✅ Done |
| 1.3 | Auth with Microsoft Entra ID (Admin vs. User roles) | ⬜ Not started |
| 1.4 | CI/CD pipeline (GitHub Actions → Azure) | ⬜ Not started |

---

## Epic 2 — Video Ingestion & Frame Extraction

| # | Story | Status | Notes |
|---|---|---|---|
| 2.1 | Admin upload UI (drag & drop video) | ⬜ Not started | Upload to Blob Storage with SAS tokens |
| 2.2 | Azure Function: extract keyframes from video | ⬜ Not started | FFmpeg in container; triggered by Blob event |
| 2.3 | Store frames in Blob, metadata in Cosmos SQL | ⬜ Not started | Frame index, timestamp, blob URI |

---

## Epic 3 — AI Vision Analysis & Feature Extraction

| # | Story | Status | Notes |
|---|---|---|---|
| 3.1 | Analyze each frame with Azure AI Vision | ⬜ Not started | Scene tags, objects, OCR text (room signs) |
| 3.2 | Generate feature vectors (embeddings) per frame | ⬜ Not started | For visual place recognition / re-localization |
| 3.3 | Detect potential POIs automatically | ⬜ Not started | Doors, signs, elevators, desks, equipment |
| 3.4 | Store analysis results + vectors in Cosmos | ⬜ Not started | |

---

## Epic 4 — Map Building & Graph Construction

| # | Story | Status | Notes |
|---|---|---|---|
| 4.1 | Build spatial graph from sequential frames | ⬜ Not started | Nodes = keyframe locations; edges = adjacency from video sequence |
| 4.2 | Admin map editor UI | ⬜ Not started | Visual graph, drag nodes, label POIs, merge duplicates |
| 4.3 | Support multiple floors / zones | ⬜ Not started | Sub-graphs linked via elevators/stairs |
| 4.4 | POI CRUD with semantic descriptions | ⬜ Not started | Stored with OpenAI embeddings for search |

---

## Epic 5 — User Localization (Point A)

| # | Story | Status | Notes |
|---|---|---|---|
| 5.1 | Camera capture (web/mobile) | ⬜ Not started | MediaDevices API or native camera |
| 5.2 | Send frame → Azure AI Vision → get feature vector | ⬜ Not started | |
| 5.3 | Match vector against graph nodes (nearest neighbor) | ⬜ Not started | Cosmos vector search or AI Search |
| 5.4 | Fallback: manual POI selection for Point A | ⬜ Not started | Dropdown / searchable list |
| 5.5 | Display current location on map | ⬜ Not started | |

---

## Epic 6 — Destination Resolution (Point B)

| # | Story | Status | Notes |
|---|---|---|---|
| 6.1 | Natural language input for destination | ⬜ Not started | "Take me to Dr. Smith's office" |
| 6.2 | Azure OpenAI: parse intent → extract destination entity | ⬜ Not started | GPT-4o with function calling |
| 6.3 | Semantic search POIs via embeddings (AI Search) | ⬜ Not started | Match parsed entity to known POIs |
| 6.4 | Disambiguation UI if multiple matches | ⬜ Not started | "Did you mean X or Y?" |
| 6.5 | Fallback: manual POI selection for Point B | ⬜ Not started | |

---

## Epic 7 — Pathfinding & Navigation

| # | Story | Status | Notes |
|---|---|---|---|
| 7.1 | Shortest path (Gremlin traversal or server-side A*) | ⬜ Not started | Weighted by distance/steps |
| 7.2 | Generate step-by-step text directions | ⬜ Not started | "Walk forward, turn left at the water fountain" |
| 7.3 | Azure OpenAI: generate human-friendly directions | ⬜ Not started | From raw path nodes → natural language |

---

## Epic 8 — Real-Time Camera Guidance

| # | Story | Status | Notes |
|---|---|---|---|
| 8.1 | Continuous camera feed with periodic re-localization | ⬜ Not started | Every N seconds, compare frame to graph |
| 8.2 | AR-style overlay (directional arrows) | ⬜ Not started | Canvas/WebGL overlay on camera feed |
| 8.3 | Progress tracking on map | ⬜ Not started | Highlight current position, remaining path |
| 8.4 | "You have arrived" detection | ⬜ Not started | |
| 8.5 | Re-routing if user deviates | ⬜ Not started | |

---

## Epic 9 — Polish & Production Readiness

| # | Story | Status | Notes |
|---|---|---|---|
| 9.1 | Mobile-responsive PWA | ⬜ Not started | Installable, offline map cache |
| 9.2 | Accessibility (screen reader nav, high contrast) | ⬜ Not started | |
| 9.3 | Rate limiting & cost guardrails for AI calls | ⬜ Not started | |
| 9.4 | Application Insights telemetry | ⬜ Not started | |
| 9.5 | Admin analytics dashboard | ⬜ Not started | Popular routes, usage stats |
│     • Continuous frame capture → re-localize             │
│     • AR overlay arrows / text instructions              │
│     • SignalR for real-time updates                      │
└──────────────────────────────────────────────────────────┘