# 🌱 Grow‑Pulse Backend — README (v0.3)

_Subproduct of **GrowRoutine**_

Grow‑Pulse is more than just code – it’s a **daily learning engine** designed to empower ambitious professionals.  
It transforms the overwhelming flood of daily news into **clear opportunities, micro‑actions, and public visibility**.

This project is also an experiment in **personal scalability**: building a product that feels like an entire editorial + coaching team, powered by **one person + AI agents**.  
It reflects the core mission of GrowRoutine: **help people grow 1% every day, consistently and visibly, to reach top‑tier opportunities**.

Grow‑Pulse delivers daily insights as structured JSON that can be consumed by any frontend (Next.js, mobile apps, dashboards).  
It is intentionally built lean, modular, and agent‑first – to explore how far a single individual can go when amplified by AI.

---

## 🔧 Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for fast, isolated env + runner)
- An OpenAI API key exported as `OPENAI_API_KEY` (see **Configuration**)

---

## 🚀 Run locally with uv

### 1) Clone the project
```bash
git clone https://github.com/youruser/growpulse-backend.git
cd growpulse-backend
```

### 2) Create the environment and install dependencies
```bash
uv sync
```
This installs everything from `pyproject.toml` / `requirements.txt` into a virtual env managed by `uv`.

### 3) Run the FastAPI server
```bash
uv run uvicorn api.main:app --reload
```
- Live API: http://127.0.0.1:8000  
- Swagger UI: http://127.0.0.1:8000/docs

### 4) Real example execution (works today, can be improved)
**Request**
```bash
curl -X POST http://127.0.0.1:8000/grow-pulse \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Daily briefing",
    "lang": "en",
    "profession": "Developer",
    "sector": "AI"
  }'
```

**Sample response (abridged)**
```json
{
  "news": "1) OpenAI's GPT-4 Turbo ... 2) Anthropic's Claude 2 ... 3) DeepMind AlphaFold ... 4) Open-Source AI movement ... 5) Enterprise AI adoption ...",
  "meaning": "As a .NET + AWS + LLM-agents Tech Lead, each item presents opportunities across finance, insurance, healthcare, travel, energy...",
  "action": "Create a short LinkedIn post summarizing today’s key insight...",
  "linkedin_post": "🌟 Embracing the Future of AI Across Industries 🌟 ...",
  "poc_ideas": "POC 1: GPT-4 Turbo API integration ... POC 2: Safety analyzer with Claude 2 ... POC 3: AlphaFold visualization ...",
  "compounding": "Strategy to reach +$10K/mo via posts, actions, and POCs ...",
  "final_summary": "Condensed takeaways and next steps ..."
}
```
> Notes: content varies per run; the above is a shortened, real‑world style output.


### 5) Run in JupyterLab (optional)
```bash
uv run jupyter lab
```
Select the `growpulse-backend` kernel and run:
```python
import nest_asyncio, uvicorn
from api.main import app
nest_asyncio.apply()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

✅ Quick start in one line:
```bash
uv sync && uv run uvicorn api.main:app --reload
```

---

## ⚙️ Configuration

The backend expects an OpenAI API key at runtime.

### Option A) Export in your shell (recommended)
**macOS/Linux**
```bash
export OPENAI_API_KEY="sk-..."
```
**Windows PowerShell**
```powershell
$Env:OPENAI_API_KEY="sk-..."
```

### Option B) `.env` file
If you prefer a `.env` file, ensure your app loads it (e.g., with `python-dotenv`). Python does **not** read `.env` automatically:
```python
# early in your startup (e.g., api/main.py)
from dotenv import load_dotenv
load_dotenv()
```
Then create `.env` at repo root:
```
OPENAI_API_KEY=sk-...
```

Optional envs you may add later:
```
MODEL_NAME=gpt-4o
LOG_LEVEL=INFO
```

---

## 🧱 API

- `POST /grow-pulse` — Generate the daily briefing
  - Body:
    ```json
    {
      "task": "Daily briefing",
      "lang": "en",
      "profession": "Developer",
      "sector": "AI"
    }
    ```
  - Returns: structured JSON with the fields shown in the sample above.

---

## 🖥️ Consuming from the Next.js frontend

Public repo: **growpulse-frontend** → https://github.com/mejorandro/growpulse-frontend

Minimal fetch example (Server Action / Route Handler or server component):
```ts
// api/growpulse.ts (example)
export async function getDailyBriefing() {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
  const res = await fetch(`${base}/grow-pulse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task: "Daily briefing",
      lang: "en",
      profession: "Developer",
      sector: "AI"
    }),
    // If calling from the browser and your backend is on a different origin,
    // make sure CORS is enabled in FastAPI (see below).
  });
  if (!res.ok) throw new Error(`GrowPulse error: ${res.status}`);
  return await res.json();
}
```

In **FastAPI**, enable CORS if the frontend runs on a different origin (e.g., `http://localhost:3000`):
```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Suggested `.env.local` for Next.js:
```
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

## 🧪 Extra: HTTPie & Python snippets

**HTTPie**
```bash
http :8000/grow-pulse task="Daily briefing" lang="en" profession="Developer" sector="AI"
```

**Python (requests)**
```python
import requests, json
payload = {
  "task": "Daily briefing",
  "lang": "en",
  "profession": "Developer",
  "sector": "AI"
}
r = requests.post("http://127.0.0.1:8000/grow-pulse", json=payload, timeout=60)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
```

---

## 🛠️ Troubleshooting

- **307 Temporary Redirect** when posting to `/grow-pulse`  
  FastAPI may redirect between `/grow-pulse` and `/grow-pulse/`. Most clients follow `307` automatically. If yours doesn’t, call the exact path your route defines (this project uses `/grow-pulse`).

- **500 Internal Server Error** at startup or first request  
  Usually missing `OPENAI_API_KEY` or not loaded. Export it in the shell, or load a `.env` file with `python-dotenv` (see **Configuration**).

- **CORS errors** in the browser console  
  Enable `CORSMiddleware` in FastAPI and list your frontend origin (see snippet above).

- **Windows PowerShell & venv activation errors**  
  Using `uv` avoids manual venv activation. Always run with `uv run <cmd>`.

---

## 🧭 Roadmap (short)
- Streaming responses (Server‑Sent Events) for real‑time UI.
- More profession/sector presets.
- Better summarization knobs (depth, tone, length).
- Auth & rate‑limits for multi‑user deployments.
- Observability: tracing + structured logs.

---

## 📄 License
MIT (tbd).