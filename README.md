---

# 📖 README – **growpulse-backend**

```markdown
# 🌱 GrowPulse Backend

**GrowPulse Backend** is the analytics and agent engine for the **GrowRoutine ecosystem**.  
It powers the daily insights delivered by the frontend app, fetching news, generating opportunities, and suggesting profession‑specific actions.

---

## 🚀 Features
- 📰 Fetch dynamic news (by **profession** + **focus area/sector**)
- 💡 Translate news into career opportunities & key takeaways
- ⚡ Generate **daily micro‑actions (≤ 15 min)**
- 🔗 Produce **bilingual (EN/ES) LinkedIn** post drafts
- 🛠️ Suggest **3 mini‑POC/portfolio ideas** per day (time‑boxed ~45m)
- 📈 Explain **compounding strategies** for career growth (habits, portfolio, network)
- 🌐 Multi‑language (English / Spanish)
- 🔌 Exposed via **FastAPI** endpoints

---

## 📂 Project Structure
- **agents/** → LangChain/LangGraph agent graphs (`daily_reader.py`)
- **api/** → FastAPI app (`main.py`) + routes (`readings.py`, `health.py`)
- **models/** → Pydantic schemas & ORM models
- **services/** → provider adapters (search/news), prompt templates, orchestration
- **tests/** → Unit tests
- `requirements.txt`, `Dockerfile`, `README.md`

```

backend/
agents/
daily\_reader.py
api/
main.py
routes/
readings.py
health.py
models/
reading.py
source.py
services/
search\_providers.py
templating.py
generate.py
tests/
test\_readings.py
requirements.txt
Dockerfile
README.md

````

---

## 🛠️ Tech Stack
- **FastAPI** – API framework
- **LangChain + LangGraph** – agent orchestration
- **OpenAI / Local LLMs** – AI models (pluggable)
- **HTTP clients (requests/httpx)** – dynamic news/search fetching
- **Pydantic** – input/output validation
- **SQLite (dev) / Postgres (prod)** – persistence
- **Docker** – containerized deployments

---

## ⚡ Run Locally

1) **Clone the repo**
```bash
git clone https://github.com/mejorandro/growpulse-backend.git
cd growpulse-backend
````

2. **Environment variables**

```bash
cp .env.example .env
```

**.env example**

```
# LLMs
OPENAI_API_KEY=
# Optional providers (the app will pick what’s available)
TAVILY_API_KEY=
EXA_API_KEY=
SERPAPI_API_KEY=
NEWSAPI_API_KEY=

# Server & CORS
APP_ENV=local
TZ=America/Costa_Rica
ALLOW_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=sqlite:///./.data/growpulse.db
```

3. **Create virtual env & install deps**

* **macOS/Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

* **Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If you hit policy errors, run in the same shell:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m pip install -U pip
pip install -r requirements.txt
```

4. **Run the API**

```bash
uvicorn api.main:app --reload --port 8000
```

Open docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 REST API (v1)

### POST `/api/v1/readings/generate`

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
  "title": "On-device AI and the new edge pattern",
  "summary": "...",
  "key_points": ["..."],
  "actions_for_you": ["..."],
  "mini_poc_ideas": [{"title": "...", "timebox": "45m", "outline": ["..."]}],
  "sources": [{"title": "...", "url": "...", "publisher": "...", "published_at": "..."}],
  "profession": "Tech Lead (.NET)",
  "focus_area": "AI agents in production",
  "created_at": "2025-08-27T17:20:00Z"
}
```

### GET `/api/v1/readings`

Query by `date`, `profession`, `focus_area`.

### GET `/api/v1/readings/{id}`

Fetch a previously generated reading.

### GET `/api/v1/health`

Liveness/readiness.

**cURL quickstart**

```bash
curl -X POST http://localhost:8000/api/v1/readings/generate \
  -H 'Content-Type: application/json' \
  -d '{"profession":"Tech Lead (.NET)","focus_area":"AI agents in production","top_n_sources":5}'
```

---

## 🧪 Quality

* **Tests:** `pytest -q`
* **Lint/Format:** `ruff check .` and `black --check .`
* **Type hints:** Python 3.12 + Pydantic models

---

## 🐳 Docker

```bash
docker build -t growpulse-backend .
docker run -p 8000:8000 --env-file .env growpulse-backend
```

---

## 🔒 Security & Privacy (WIP)

* Local dev: no auth. Prod: JWT/OAuth recommended.
* Avoid sending proprietary data to external LLMs without approval.
* Respect provider terms and robots.txt.

---

## 🗺️ Roadmap

* [ ] Auth (JWT) + user profiles
* [ ] Postgres + migrations
* [ ] Background jobs for scheduled daily briefs
* [ ] Observability (OpenTelemetry + metrics)
* [ ] Caching & rate limiting
* [ ] Provider contract tests

---

## 📌 For Hiring Managers

* **Problem:** Busy engineers need a *daily pulse* that converts news → actions.
* **This backend:** Orchestrates search + reasoning, outputs consistent JSON with actions & mini‑POCs.
* **Status:** Active WIP, locally functional. Clear path to prod hardening.

```
```
