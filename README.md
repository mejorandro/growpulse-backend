# GrowPulse — Backend & Frontend READMEs (WIP)

> **Purpose (for hiring managers):** GrowPulse is an AI‑curated daily reading & action engine for busy engineers and tech leads. It ingests today’s top tech/business stories, summarizes them in clear English, and outputs **actionable, role‑aware briefs** with **mini POC ideas you can build in ~45 minutes**. Built with **FastAPI + LangChain/LangGraph** on the backend and **Next.js + TypeScript** on the frontend. Fully local dev, container‑ready, with a clear roadmap toward production.

---

Below you’ll find **two complete README files** you can drop into `/backend/README.md` and `/frontend/README.md`. They’re written to be useful for evaluators and practical for developers.

---

## `/backend/README.md`

# GrowPulse • Backend (FastAPI + LangChain) — WIP

> **One‑liner:** AI service that turns today’s tech/business news into role‑aware daily readings with takeaways and 45‑minute POC ideas.

## Highlights
- **FastAPI** service exposing clean JSON endpoints
- **LangChain/LangGraph** pipelines for retrieval + reasoning
- **Pluggable search/ingestion** providers (e.g., web search APIs or curated RSS)
- **Deterministic structure**: summary → insights → actions → mini POCs → sources
- **SQLite** persistence (local dev) with a migration path to Postgres
- **Typed Python 3.12**, linted & tested (Ruff/Black/Pytest)

## Architecture
```
app/
  main.py                 # FastAPI app & router registration
  api/                    # versioned routes
    v1/
      readings.py         # /generate, /readings endpoints
      health.py           # /health
  core/
    config.py             # settings (Pydantic)
    db.py                 # SQLAlchemy session/engine
    logging.py            # structured logs
  models/
    reading.py            # ORM models (Reading, Source)
  services/
    generate.py           # LangChain/LangGraph pipeline orchestration
    search_providers.py   # adapters (Tavily/Exa/SerpAPI/RSS)
    templating.py         # prompt templates & output schema
  utils/
    time.py               # timezone helpers
    ids.py                # ULIDs/UUIDs
  tests/
    test_readings.py
```

### Data Model (simplified)
- **Reading**: id, date, profession, focus_area, title, summary, key_points[], actions[], mini_poc_ideas[], sources[], created_at
- **Source**: title, url, publisher, published_at, relevance_score

## API (v1)

### `POST /api/v1/readings/generate`
Generate a new reading for a given **profession** and **focus area**.

**Body**
```json
{
  "profession": "Tech Lead (.NET)",
  "focus_area": "AI agents in production",
  "top_n_sources": 5,
  "date": "2025-08-27"  
}
```

**Response (shape)**
```json
{
  "id": "rdng_01J...",
  "title": "On‑device AI and the new edge pattern",
  "summary": "…",
  "key_points": ["…", "…"],
  "actions_for_you": [
    "Audit one workflow for agent hand‑offs",
    "Add guardrails on tool invocation latency"
  ],
  "mini_poc_ideas": [
    {
      "title": "45‑min POC: Agent tool sandbox",
      "timebox": "45m",
      "outline": ["Scaffold FastAPI endpoint", "Add mock tool", "Trace with LangSmith"]
    }
  ],
  "sources": [{"title": "…", "url": "…", "publisher": "…", "published_at": "…"}],
  "profession": "Tech Lead (.NET)",
  "focus_area": "AI agents in production",
  "created_at": "2025-08-27T17:20:00Z"
}
```

### `GET /api/v1/readings/{id}`
Return a previously generated reading.

### `GET /api/v1/readings?date=YYYY-MM-DD&profession=...&focus_area=...`
List readings (filterable by date/profession/focus).

### `GET /api/v1/health`
Liveness/readiness check.

## Local Development

### Prerequisites
- **Python 3.12**
- **uvicorn** (installed via `requirements.txt`)

### 1) Clone & env
```bash
git clone https://github.com/<your‑user>/growpulse.git
cd growpulse/backend
cp .env.example .env
```

**`.env` (example)**
```
# LLM
OPENAI_API_KEY=
# Optional, pick any you have keys for (the service picks what’s available)
TAVILY_API_KEY=
EXA_API_KEY=
SERPAPI_API_KEY=
NEWSAPI_API_KEY=

# Email delivery (optional, for future weekly digests)
SENDGRID_API_KEY=

# DB & server
DATABASE_URL=sqlite:///./.data/growpulse.db
ALLOW_ORIGINS=http://localhost:3000
PYTHONUNBUFFERED=1
APP_ENV=local
TZ=America/Costa_Rica
```

### 2) Virtualenv & install
**macOS/Linux**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If you see a policy error, run this once in the same shell:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m pip install -U pip
pip install -r requirements.txt
```

### 3) Run
```bash
uvicorn app.main:app --reload --port 8000
```
FastAPI docs: http://localhost:8000/docs

## Testing & Linting
```bash
pytest -q
ruff check .
black --check .
```

## Provider Strategy
The backend tries providers in order of availability: **Exa/Tavily/SerpAPI → curated RSS fallback**. You can control this in `services/search_providers.py`.

## Security & Privacy
- No authentication for local dev; add API key or OAuth for prod.
- Don’t send proprietary/customer data to external LLMs without approvals.
- Respect robots.txt and provider terms; avoid paywalled sources.

## Roadmap
- [ ] Auth (JWT) + user profiles
- [ ] Postgres + Prisma/SQLAlchemy migrations
- [ ] Background jobs (scheduled daily briefs)
- [ ] Observability (OpenTelemetry + Prometheus/Grafana)
- [ ] Rate limiting & caching layer
- [ ] Unit + contract tests for provider adapters

## License
WIP — private project (not open‑sourced yet).

---

## `/frontend/README.md`

# GrowPulse • Frontend (Next.js + TypeScript) — WIP

> **One‑liner:** Minimal, fast UI to browse today’s curated readings with key takeaways, actions, and quick POC ideas.

## Highlights
- **Next.js (App Router) + TypeScript**
- **Tailwind + shadcn/ui + Framer Motion** for a clean, modern UX
- **API‑first**: reads from the backend `v1` endpoints
- **Accessible & responsive** by default

## Screens & Routes (MVP)
- `/` — landing: what GrowPulse is & how it helps busy engineers
- `/readings` — list view with filters (date, profession, focus)
- `/reading/[id]` — detailed brief (summary, actions, mini‑POCs, sources)

## Architecture
```
src/
  app/
    layout.tsx
    page.tsx               # landing
    readings/
      page.tsx             # list
    reading/[id]/
      page.tsx             # detail
  components/
    ReadingCard.tsx
    SourceList.tsx
    Filters.tsx
    Header.tsx
    Footer.tsx
  lib/
    api.ts                 # fetch helpers
    config.ts              # env & constants
  styles/
    globals.css
```

## Local Development

### Prerequisites
- **Node.js 20+**
- **pnpm** (recommended) or npm

### 1) Clone & env
```bash
cd growpulse/frontend
cp .env.example .env.local
```

**`.env.local` (example)**
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BRAND_NAME=GrowPulse
```

### 2) Install & run
```bash
pnpm i
pnpm dev
# or
npm i
npm run dev
```
App: http://localhost:3000

## Styling & Components
- Typography & spacing follow a **minimal, editorial** aesthetic.
- Use **shadcn/ui** for consistent primitives (Buttons, Cards, Skeletons).
- Motion is subtle (fade/slide) with Framer Motion.

## Scripts
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

## Connecting to the Backend
The frontend reads `NEXT_PUBLIC_API_BASE_URL` and calls:
- `GET /api/v1/readings?date=...` for the list
- `GET /api/v1/readings/{id}` for the detail
- `POST /api/v1/readings/generate` (dev‑only) to generate a new brief

`lib/api.ts` wraps `fetch` with error handling and simple response validation.

## Testing & Quality
- Unit/UI tests (planned) with **Vitest + Testing Library**
- E2E (planned) with **Playwright**
- Linting via **ESLint**; formatting via **Prettier**

## Roadmap
- [ ] Auth guard + saved profiles
- [ ] Skeleton states and optimistic updates
- [ ] Shareable links & social preview cards
- [ ] Light/Dark theme toggle
- [ ] Simplified offline mode (cache last brief)

## Deploy Targets
- **Vercel** (static + serverless) or any Node host
- Point to your backend base URL via `NEXT_PUBLIC_API_BASE_URL`

## License
WIP — private project (not open‑sourced yet).

---

## Top‑Level (optional) Docker Compose

For a one‑command local stack:
```yaml
# docker-compose.yml (optional)
version: '3.9'
services:
  backend:
    build: ./backend
    env_file: ./backend/.env
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000
    ports: ["3000:3000"]
    depends_on: [backend]
```

Run: `docker compose up --build`

---

## Hiring‑Oriented Summary
- **Problem:** Busy tech leaders need a *daily* pulse on AI/tech that translates to action.
- **Solution:** GrowPulse curates today’s news → outputs role‑aware briefs with clear next steps and tiny POCs.
- **Why me:** I built an end‑to‑end system (backend reasoning + frontend UX) with production‑ready patterns: typed code, testing, adapters, and a pragmatic roadmap.

> **Status:** Active WIP. Local dev works end‑to‑end. Provider adapters and auth/observability are next. If you’d like to see the internals or run a short demo, I can walk through the pipeline and design decisions.

