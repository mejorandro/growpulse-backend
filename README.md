# 🌱 Grow-Pulse Backend
_Subproduct of **GrowRoutine**_

Grow-Pulse is more than just code – it is a **daily learning engine** designed to empower ambitious professionals.  
It transforms the overwhelming flood of daily news into **clear opportunities, micro-actions, and public visibility**.  

This project is also an experiment in **personal scalability**: building a product that feels like an entire editorial and coaching team, but powered only by **one person + AI agents**.  
It reflects the core mission of GrowRoutine: **help people grow 1% every day, consistently and visibly, to reach top-tier opportunities**.  

Grow-Pulse delivers daily insights as structured JSON that can be consumed by any frontend (Next.js, mobile apps, dashboards).  
It is intentionally built lean, modular, and agent-first – to challenge the idea of how far a single individual can go when amplified by AI.  

---

## 🚀 Run locally with uv

### 1. Clone the project
```bash
git clone https://github.com/youruser/growpulse-backend.git
cd growpulse-backend
```

### 2. Create the environment and install dependencies
```bash
uv sync
```

👉 This will automatically install all dependencies listed in `pyproject.toml` and `requirements.txt`.

### 3. Run the FastAPI server
```bash
uv run uvicorn api.main:app --reload
```

- Live API: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Test a request
```bash
curl -X POST http://127.0.0.1:8000/grow-pulse/ \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Daily briefing",
    "lang": "en",
    "profession": "Developer",
    "sector": "AI"
  }'
```

Expected JSON response:
```json
{
  "news": "...",
  "meaning": "...",
  "action": "...",
  "linkedin_post": "...",
  "poc_ideas": "...",
  "compounding": "...",
  "final_summary": "..."
}
```

### 5. Run in JupyterLab (optional)
```bash
uv run jupyter lab
```

Select the `growpulse-backend` kernel and create a notebook.  
Inside a cell you can run the FastAPI server with:

```python
import nest_asyncio, uvicorn
from api.main import app

nest_asyncio.apply()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

✅ With this setup, your environment is ready and anyone can run it using just:
```bash
uv sync && uv run uvicorn api.main:app --reload
```

---

## ✨ Why Grow-Pulse Matters

- **For professionals**: It gives you a daily 10-minute briefing you can act on immediately.  
- **For recruiters & companies**: It demonstrates how AI can generate *clarity + action* instead of noise.  
- **For builders**: It proves that one person with the right agents can create scalable impact without a large team.  

Grow-Pulse is not just another AI demo.  
It is a statement: **the future of personal growth and professional branding will be built by small teams amplified by intelligent agents**.  
