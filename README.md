# JourneyForge: Enterprise B2B Marketing Journey Builder

JourneyForge is an enterprise-scale application for creating, managing, and collaborating on B2B customer journey maps. It empowers marketing teams to visualize their customer lifecycles across distinct stages (Awareness, Consideration, Decision, etc.), map personas to journeys, and leverage AI to generate strategic content and touchpoints.

## Key Features

- **Interactive Journey Canvas:** A horizontally scrollable drag-and-drop canvas built with `@dnd-kit/core` to visualize and reorder journey stages seamlessly.
- **Enterprise Security & RBAC:** Multi-tenant architecture with JWT-based authentication and role-based access control (Admin, Editor, Viewer).
- **Real-Time Collaboration:** WebSocket integration to see who is currently viewing or editing the same journey map.
- **AI-Powered Suggestions:** Integration with Google's GenAI to automatically suggest stage goals, touchpoints, and persona details based on context.
- **Advanced Persona Management:** Create robust buyer personas and link them to specific journey maps.
- **Analytics & Reporting:** Visual dashboards (using Recharts) to track team activity and journey completion metrics.
- **Export Capabilities:** Export journey maps directly to PDF, CSV, and JSON for offline sharing and presentations.

---

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- Docker & Docker Compose (for MySQL)

### 1. Database Setup
Start the MySQL database using Docker Compose:
```bash
docker-compose up -d
```

### 2. Backend Setup (FastAPI)
Navigate to the `backend` directory, create a virtual environment, and start the API server:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```
> **Note:** To enable AI features, ensure you have a `GEMINI_API_KEY` defined in `backend/.env`. The system will gracefully mock AI responses if the key is missing.

### 3. Frontend Setup (Next.js)
Navigate to the `frontend` directory and start the development server:
```bash
cd frontend
npm install
npm run dev
```
Access the application at [http://localhost:3000](http://localhost:3000).

---

## Testing

The project includes comprehensive test coverage for both the frontend and backend.

**Backend Tests:**
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest -v
```

**Frontend Tests:**
```bash
cd frontend
npx vitest run
```

---

## Documentation

For a detailed breakdown of the application design, technical choices, and schema, please see [ARCHITECTURE.md](ARCHITECTURE.md).
