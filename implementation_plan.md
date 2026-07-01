# JourneyForge — Enterprise B2B Customer Journey Mapping Platform

Revised implementation plan for an enterprise-scale application inspired by [Ruler Analytics' customer journey mapping guide](https://www.ruleranalytics.com/blog/analytics/customer-journey-mapping-4/).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 15 (Frontend)                     │
│          TypeScript · Tailwind v4 · Zustand · Recharts       │
│          WebSocket client · NextAuth.js · React DnD           │
├─────────────────────────────────────────────────────────────┤
│                         REST + WS                            │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI (Backend)                          │
│     Python · SQLAlchemy · Alembic · Pydantic · JWT Auth      │
│     WebSocket server · Google Gemini API · ReportLab          │
├─────────────────────────────────────────────────────────────┤
│                      MySQL Database                          │
│            Users · Teams · Journeys · Personas               │
│         Stages · Goals · Touchpoints · Audit Logs            │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15, TypeScript | SSR, API routes, routing |
| **Styling** | Tailwind CSS v4 | Utility-first enterprise UI |
| **State** | Zustand | Client-side state management |
| **Charts** | Recharts | Dashboard analytics visualizations |
| **DnD** | @dnd-kit | Drag-and-drop journey builder |
| **Real-time** | WebSocket (native) | Live collaboration |
| **Backend** | FastAPI (Python) | REST API + WebSocket server |
| **ORM** | SQLAlchemy 2.0 | Type-safe database access |
| **Migrations** | Alembic | Schema versioning |
| **Database** | MySQL 8 | Persistent storage |
| **Auth** | JWT (PyJWT) + bcrypt | Token-based auth with RBAC |
| **AI** | Google Gemini API | Smart suggestions for goals/content |
| **Export** | ReportLab + Pillow | PDF/PNG generation |
| **Validation** | Pydantic v2 | Request/response schemas |

---

## Open Questions

> [!IMPORTANT]
> **MySQL Instance**: Do you already have a MySQL server running locally, or should we include Docker Compose for spinning up MySQL alongside the backend?

> [!IMPORTANT]
> **Gemini API Key**: The AI suggestions feature requires a Google Gemini API key. Do you have one, or should we make this feature optional with a fallback?

> [!IMPORTANT]
> **Deployment**: Are we targeting local development only for now, or do you need Docker + deployment configs (e.g., Vercel for frontend, a cloud VM for FastAPI)?

---

## Directory Structure

```
b2b-marketing/
├── frontend/                          # Next.js application
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── app/                       # App Router
│   │   │   ├── layout.tsx             # Root layout (fonts, providers)
│   │   │   ├── page.tsx               # Landing / redirect
│   │   │   ├── globals.css            # Tailwind imports + custom tokens
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx         # Authenticated layout (navbar, sidebar)
│   │   │   │   ├── dashboard/page.tsx # Main dashboard
│   │   │   │   ├── journeys/
│   │   │   │   │   ├── page.tsx       # Journey list
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx   # Journey builder
│   │   │   │   ├── personas/page.tsx  # Persona manager
│   │   │   │   ├── analytics/page.tsx # Analytics dashboard
│   │   │   │   └── settings/page.tsx  # Team & account settings
│   │   ├── components/
│   │   │   ├── ui/                    # Reusable primitives
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   ├── Dropdown.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Avatar.tsx
│   │   │   │   ├── Tabs.tsx
│   │   │   │   └── Spinner.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── AuthGuard.tsx
│   │   │   ├── journey/
│   │   │   │   ├── JourneyCanvas.tsx  # Main builder canvas
│   │   │   │   ├── StageCard.tsx      # Draggable stage card
│   │   │   │   ├── StageConnector.tsx # SVG connectors
│   │   │   │   ├── DetailPanel.tsx    # Goal/touchpoint/content editor
│   │   │   │   ├── StageForm.tsx      # Add/edit stage modal
│   │   │   │   └── JourneyCard.tsx    # Journey list card
│   │   │   ├── persona/
│   │   │   │   ├── PersonaCard.tsx
│   │   │   │   ├── PersonaForm.tsx
│   │   │   │   └── PersonaWidget.tsx  # Builder sidebar widget
│   │   │   ├── analytics/
│   │   │   │   ├── FunnelChart.tsx
│   │   │   │   ├── StageMetrics.tsx
│   │   │   │   ├── ConversionChart.tsx
│   │   │   │   └── ActivityFeed.tsx
│   │   │   └── collaboration/
│   │   │       ├── PresenceCursors.tsx # Show other users' cursors
│   │   │       ├── ActiveUsers.tsx    # Who's online indicator
│   │   │       └── ChangeIndicator.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useJourneys.ts
│   │   │   ├── usePersonas.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAISuggestions.ts
│   │   │   └── useExport.ts
│   │   ├── stores/
│   │   │   ├── authStore.ts
│   │   │   ├── journeyStore.ts
│   │   │   ├── personaStore.ts
│   │   │   └── collaborationStore.ts
│   │   ├── lib/
│   │   │   ├── api.ts                 # Axios/fetch wrapper
│   │   │   ├── websocket.ts           # WS client class
│   │   │   └── utils.ts              # Helpers (dates, IDs, etc.)
│   │   └── types/
│   │       ├── journey.ts
│   │       ├── persona.ts
│   │       ├── user.ts
│   │       └── api.ts
│
├── backend/                           # FastAPI application
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                  # Migration files
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── config.py                  # Settings (env vars)
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── journey.py
│   │   │   ├── stage.py
│   │   │   ├── persona.py
│   │   │   └── audit_log.py
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── journey.py
│   │   │   ├── stage.py
│   │   │   ├── persona.py
│   │   │   └── common.py
│   │   ├── routers/                   # API route modules
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── journeys.py
│   │   │   ├── stages.py
│   │   │   ├── personas.py
│   │   │   ├── analytics.py
│   │   │   ├── ai.py
│   │   │   ├── export.py
│   │   │   └── websocket.py
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── journey_service.py
│   │   │   ├── persona_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── export_service.py
│   │   │   └── collaboration_service.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # JWT verification middleware
│   │   │   └── rbac.py                # Role-based access control
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py            # Password hashing, JWT utils
│   │       └── helpers.py
│
├── docker-compose.yml                 # MySQL + backend + frontend
└── README.md
```

---

## Proposed Changes

### Phase 1: Project Scaffolding & Infrastructure

#### Frontend Setup
- Initialize Next.js 15 with TypeScript in `frontend/`
- Install dependencies: `zustand`, `recharts`, `@dnd-kit/core`, `@dnd-kit/sortable`, `axios`, `lucide-react`
- Configure Tailwind CSS v4 with custom design tokens (dark palette, typography scale)
- Set up path aliases (`@/components`, `@/hooks`, `@/stores`, etc.)

**Steps to code:**
1. `npx -y create-next-app@latest frontend/ --typescript --tailwind --eslint --app --src-dir --no-import-alias`
2. Install additional packages
3. Configure `tailwind.config.ts` with enterprise color palette & theme extensions
4. Set up `globals.css` with Tailwind layers + custom CSS variables
5. Create root `layout.tsx` with `Inter` + `Outfit` fonts, dark mode, and provider wrappers

#### Backend Setup
- Initialize FastAPI project in `backend/` with `pyproject.toml`
- Install: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pymysql`, `pydantic`, `pyjwt`, `bcrypt`, `python-dotenv`, `google-generativeai`, `reportlab`, `Pillow`
- Configure database connection, Alembic migrations, CORS

**Steps to code:**
1. Create `pyproject.toml` with all dependencies
2. Create `app/config.py` loading env vars (DB URL, JWT secret, Gemini key)
3. Create `app/database.py` with SQLAlchemy async engine + session factory
4. Create `app/main.py` with CORS, router includes, startup/shutdown events
5. Init Alembic with `alembic init alembic`, configure `env.py` for SQLAlchemy

#### Docker Compose
- MySQL 8 container with volume persistence
- Backend container (FastAPI + Uvicorn)
- Frontend container (Next.js dev server)
- Shared network

---

### Phase 2: Database Schema & Models

#### MySQL Schema (via SQLAlchemy models)

```sql
-- Users & Teams
users (id, email, password_hash, name, avatar_url, role, team_id, created_at, updated_at)
teams (id, name, slug, plan, created_at)
team_invitations (id, team_id, email, role, token, expires_at, accepted_at)

-- Journeys
journeys (id, team_id, name, description, status, created_by, created_at, updated_at)
journey_collaborators (journey_id, user_id, role, joined_at)

-- Stages (ordered within a journey)
stages (id, journey_id, name, description, icon, color, position, created_at, updated_at)
stage_goals (id, stage_id, text, position)
stage_touchpoints (id, stage_id, text, position)
stage_content (id, stage_id, text, content_type, position)

-- Personas
personas (id, team_id, name, role_title, company_size, goals, pain_points, motivations,
          avatar_color, created_by, created_at, updated_at)
journey_personas (journey_id, persona_id)

-- Analytics & Audit
audit_logs (id, team_id, user_id, action, entity_type, entity_id, details, created_at)
journey_snapshots (id, journey_id, snapshot_data, created_by, created_at)  -- version history
```

**Steps to code:**
1. Create SQLAlchemy models in `app/models/` for each table
2. Define relationships (Journey → Stages → Goals, Team → Users, etc.)
3. Create Pydantic schemas in `app/schemas/` for request/response validation
4. Generate initial Alembic migration
5. Run migration to create tables

---

### Phase 3: Authentication & RBAC

#### Backend — `routers/auth.py` + `services/auth_service.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create account + team |
| `/api/auth/login` | POST | Return JWT access + refresh tokens |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/invite` | POST | Invite team member (admin only) |

**RBAC Roles:**
- **Admin**: Full CRUD on all team resources, manage members, billing
- **Editor**: Create/edit journeys and personas, cannot manage team
- **Viewer**: Read-only access to all journeys and analytics

**Steps to code:**
1. Implement `security.py` — password hashing (bcrypt), JWT encode/decode (PyJWT)
2. Create `auth.py` middleware — extract & verify JWT from `Authorization` header
3. Create `rbac.py` middleware — role-checking dependency (`require_role("admin")`)
4. Build auth endpoints with Pydantic request/response models
5. Add rate limiting on login endpoint

#### Frontend — Auth pages + `AuthGuard`
1. Build `/login` and `/register` pages with form validation
2. Create `authStore.ts` (Zustand) to hold user, tokens, team
3. Create `useAuth` hook wrapping store + API calls
4. Build `AuthGuard` component that redirects unauthenticated users
5. Store tokens in httpOnly cookies (via Next.js API route proxy) or localStorage

---

### Phase 4: Journey CRUD API

#### Backend — `routers/journeys.py` + `services/journey_service.py`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/journeys` | GET | Editor+ | List team journeys |
| `/api/journeys` | POST | Editor+ | Create journey |
| `/api/journeys/{id}` | GET | Viewer+ | Get journey with stages |
| `/api/journeys/{id}` | PUT | Editor+ | Update journey metadata |
| `/api/journeys/{id}` | DELETE | Admin | Delete journey |
| `/api/journeys/{id}/stages` | GET | Viewer+ | List stages |
| `/api/journeys/{id}/stages` | POST | Editor+ | Add stage |
| `/api/journeys/{id}/stages/reorder` | PUT | Editor+ | Reorder stages |
| `/api/stages/{id}` | PUT | Editor+ | Update stage |
| `/api/stages/{id}` | DELETE | Editor+ | Delete stage |
| `/api/stages/{id}/goals` | POST/PUT/DELETE | Editor+ | Manage goals |
| `/api/stages/{id}/touchpoints` | POST/PUT/DELETE | Editor+ | Manage touchpoints |
| `/api/stages/{id}/content` | POST/PUT/DELETE | Editor+ | Manage content |

**Steps to code:**
1. Create `journey_service.py` with CRUD operations using SQLAlchemy
2. Build router endpoints with Pydantic models and RBAC dependencies
3. Include audit logging on all write operations
4. Add pagination and filtering on list endpoints
5. Return nested data (journey → stages → goals/touchpoints/content) on GET

---

### Phase 5: Frontend — Dashboard & Journey List

#### `(dashboard)/dashboard/page.tsx`
- **Stats row**: Total journeys, total personas, total team members, recent activity count
- **Journey cards grid** (glassmorphic dark cards with gradient accent borders)
- **Quick actions**: New Journey, New Persona, View Analytics
- **Recent activity feed** (last 10 audit log entries)

#### `(dashboard)/journeys/page.tsx`
- Filterable/sortable journey list
- Grid/list view toggle
- Search bar
- Bulk actions (delete, export)

**Steps to code:**
1. Create reusable UI components (`Card`, `Badge`, `Avatar`, `Spinner`, etc.)
2. Create `Navbar` and `Sidebar` layout components
3. Build `journeyStore.ts` with Zustand — holds journey list, CRUD methods
4. Create `useJourneys` hook for data fetching with SWR pattern
5. Build dashboard page with stat cards + journey grid
6. Add journey card with miniature stage preview, hover effects, staggered animations

---

### Phase 6: Frontend — Journey Builder (Core Feature)

#### `(dashboard)/journeys/[id]/page.tsx`

Full-screen workspace layout:

```
┌──────────────────────────────────────────────────────────────┐
│  Toolbar: [← Back] [Journey Name (editable)] [👥 2 online]   │
│           [🤖 AI Suggest] [📤 Export ▾] [💾 Saved]            │
├───────────┬──────────────────────────────────────────────────┤
│           │                                                  │
│  Personas │        Journey Canvas (@dnd-kit sortable)        │
│  Widget   │  ┌────────┐   ┌────────┐   ┌────────┐          │
│           │  │ Aware  │──▶│ Engage │──▶│  Sub   │──▶ ...   │
│  ─────── │  │  ness  │   │  ment  │   │ scribe │          │
│           │  └────────┘   └────────┘   └────────┘          │
│  Online   │                                                  │
│  Users    │  [+ Add Stage]                                   │
│           │                                                  │
├───────────┴──────────────────────────────────────────────────┤
│  Detail Panel (expandable):                                  │
│  [Goals] [Touchpoints] [Content]    ← tabs                   │
│  • Increase brand visibility          [✕]                    │
│  • Drive organic traffic              [✕]                    │
│  [+ Add Goal]                                                │
└──────────────────────────────────────────────────────────────┘
```

**Steps to code:**
1. Set up `@dnd-kit` with `SortableContext` for stage reordering
2. Build `StageCard.tsx` — draggable, selectable, inline-editable name
3. Build `StageConnector.tsx` — animated SVG arrows between stages
4. Build `DetailPanel.tsx` — expandable bottom panel with 3 tabs
5. Build `PersonaWidget.tsx` — sidebar showing linked personas
6. Wire up Zustand store for local edits + API sync (debounced save)
7. Add keyboard shortcuts (Delete stage, Ctrl+S to save, Escape to deselect)

---

### Phase 7: Persona System

#### Backend — `routers/personas.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/personas` | GET/POST | List/create personas |
| `/api/personas/{id}` | GET/PUT/DELETE | CRUD single persona |
| `/api/journeys/{id}/personas` | GET/POST/DELETE | Link/unlink personas |

#### Frontend — `personas/page.tsx`
- Persona card grid with avatar (initials), name, role, company size badges
- Create/edit modal with validated form
- Link personas to journeys via dropdown in builder

**Steps to code:**
1. Build backend CRUD routes + service
2. Create `PersonaForm.tsx` modal with fields: name, role, company size, goals, pain points, motivations
3. Build `PersonaCard.tsx` with glassmorphic design
4. Create `personaStore.ts` and `usePersonas` hook
5. Wire up persona linking in the journey builder sidebar

---

### Phase 8: Real-Time Collaboration

#### Backend — `routers/websocket.py` + `services/collaboration_service.py`

WebSocket protocol for live collaboration:

```json
// Client → Server
{ "type": "join_journey", "journey_id": "abc123" }
{ "type": "stage_update", "stage_id": "s1", "field": "name", "value": "Awareness" }
{ "type": "cursor_move", "x": 450, "y": 200 }

// Server → Client (broadcast to other users)
{ "type": "user_joined", "user": { "id": "u1", "name": "Alice", "avatar": "..." } }
{ "type": "stage_updated", "stage_id": "s1", "field": "name", "value": "Awareness", "by": "u1" }
{ "type": "cursor_moved", "user_id": "u1", "x": 450, "y": 200 }
{ "type": "user_left", "user_id": "u1" }
```

**Steps to code:**
1. Create WebSocket endpoint in FastAPI with connection manager (track active connections per journey)
2. Broadcast stage/goal/touchpoint changes to all connected users except sender
3. Build `useWebSocket` hook on frontend — connect, send, receive, reconnect
4. Create `collaborationStore.ts` — track online users, incoming changes
5. Build `ActiveUsers.tsx` — avatar stack showing who's online
6. Build `PresenceCursors.tsx` — colored cursors following other users (optional, can defer)
7. Merge incoming changes into local Zustand state without conflicts

---

### Phase 9: Analytics Dashboard

#### Backend — `routers/analytics.py`

Aggregate data from audit logs + journey data:
- Journey completion metrics (% of stages with goals/touchpoints/content filled)
- Team activity over time (edits per day/week)
- Stage distribution (most common stage names, average stages per journey)
- Persona coverage (% of journeys with linked personas)

#### Frontend — `analytics/page.tsx`

Charts built with Recharts:
- **Funnel chart**: Visualize the 8-stage journey as a funnel
- **Completion bar chart**: Per-journey completeness score
- **Activity line chart**: Team edits over time
- **Persona coverage donut**: Linked vs. unlinked journeys

**Steps to code:**
1. Build analytics aggregation queries in backend service
2. Create API endpoint returning aggregated stats
3. Build `FunnelChart.tsx`, `ConversionChart.tsx`, `StageMetrics.tsx` with Recharts
4. Build `ActivityFeed.tsx` — timeline of recent team actions
5. Compose analytics page layout with responsive grid

---

### Phase 10: AI Suggestions & Export

#### AI Suggestions — `routers/ai.py` + `services/ai_service.py`

Use Google Gemini API to suggest:
- **Goals** for a given stage (based on stage name + journey context)
- **Touchpoints** appropriate for the stage
- **Content types** for the stage
- **Persona refinements** based on industry/role

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/suggest/goals` | POST | Suggest goals for a stage |
| `/api/ai/suggest/touchpoints` | POST | Suggest touchpoints |
| `/api/ai/suggest/content` | POST | Suggest content types |
| `/api/ai/suggest/persona` | POST | Suggest persona details |

**Steps to code:**
1. Create `ai_service.py` with Gemini API client, crafted prompts
2. Build API endpoints accepting stage context, returning suggestions
3. Create `useAISuggestions` hook on frontend
4. Add "✨ AI Suggest" button in the DetailPanel that fills suggestions inline
5. User can accept/reject individual suggestions

#### Export — `routers/export.py` + `services/export_service.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/export/{journey_id}/json` | GET | Download journey as JSON |
| `/api/export/{journey_id}/csv` | GET | Download stages/goals as CSV |
| `/api/export/{journey_id}/pdf` | GET | Generate PDF report |
| `/api/import/json` | POST | Import journey from JSON |

**Steps to code:**
1. JSON export: serialize full journey tree, return as downloadable file
2. CSV export: flatten stages → goals/touchpoints/content into rows
3. PDF export: use ReportLab to generate a styled report with stage flow diagram
4. PNG export: use `html2canvas` on frontend to capture the canvas
5. JSON import: validate + create journey from uploaded file

---

## Implementation Order

| Phase | What | Dependencies | Estimated | Status |
|-------|------|-------------|-----------|--------|
| **1** | Project scaffolding (Next.js + FastAPI + Docker) | None | ~2h | ✅ **Complete** |
| **2** | Database schema + models + migrations | Phase 1 | ~2h | ✅ **Complete** |
| **3** | Auth system (JWT + RBAC + login/register UI) | Phase 2 | ~3h | ✅ **Complete** |
| **4** | Journey CRUD API | Phase 3 | ~2h | ✅ **Complete** |
| **5** | Dashboard + Journey list UI | Phase 4 | ~3h | ✅ **Complete** |
| **6** | Journey Builder (canvas, stages, detail panel) | Phase 5 | ~4h | ✅ **Complete** |
| **7** | Persona system (backend + UI) | Phase 4 | ~2h | ✅ **Complete** |
| **8** | Real-time collaboration (WebSockets) | Phase 6 | ~3h | ✅ **Complete** |
| **9** | Analytics dashboard (charts + aggregation) | Phase 5 | ~3h | ✅ **Complete** |
| **10** | AI suggestions + Export + Full Testing Suite | Phase 6 | ~3h | ✅ **Complete** |

**Total estimated: ~27 hours of development**

> [!NOTE]
> **Implementation Status**: As of the latest update, **100%** of the originally proposed functionality has been implemented, including comprehensive backend (`pytest`) and frontend (`vitest`) test suites, PDF/CSV/JSON exports, and WebSocket collaboration.

---

## Verification Plan

### Automated Tests
- **Backend**: `pytest` + `httpx.AsyncClient` for API endpoint tests
- **Frontend**: Component tests with React Testing Library (critical flows)
- Command: `cd backend && pytest` / `cd frontend && npm test`

### Manual Verification
1. Register a new account → verify team creation + JWT tokens
2. Login → verify dashboard loads with correct team data
3. Create a journey → verify it appears in the list + DB
4. Open builder → add/reorder/delete stages via drag-and-drop
5. Edit goals, touchpoints, content → verify auto-save
6. Create personas → link to journey → verify sidebar widget
7. Open same journey in 2 browser tabs → verify real-time sync
8. Test AI suggestions → verify Gemini returns relevant goals
9. Export as JSON/CSV/PDF → verify file downloads correctly
10. Test RBAC: viewer cannot edit, editor cannot delete, admin can do all
11. Test responsive layout at mobile, tablet, desktop breakpoints
