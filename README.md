# Indoor Navigation — Interactive Map from Video

## Quick Start

### Prerequisites
- Azure CLI (`az`) installed and logged in
- Python 3.11+
- Node.js 20+
- Azure subscription

### 1. Deploy Azure Infrastructure
```powershell
.\deploy.ps1 -Environment dev
```
This provisions all Azure resources (Cosmos DB, AI Vision, OpenAI, Storage, etc.) and generates `backend/.env`.

### 2. Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
├── infra/                  # Bicep IaC templates
│   ├── main.bicep          # Main orchestrator (subscription-level)
│   ├── parameters.dev.json
│   └── modules/            # Individual resource modules
├── backend/                # Python FastAPI backend
│   └── app/
│       ├── main.py         # FastAPI app entry
│       ├── config.py       # Settings from .env
│       ├── routers/        # API endpoints
│       └── services/       # Azure SDK integrations
├── frontend/               # React + Vite + TypeScript
│   └── src/
│       ├── App.tsx         # Router setup
│       └── pages/          # Page components
├── functions/              # Azure Functions (video processing)
│   └── function_app.py     # Blob-triggered frame extraction
└── deploy.ps1              # One-click infra deployment
```
