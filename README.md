
---

# 📖 README – **growpulse-backend**

```markdown
# 🌱 GrowPulse Backend

**GrowPulse Backend** is the analytics and agent engine for the **GrowRoutine ecosystem**.  
It powers the daily insights delivered by the frontend app, fetching news, generating opportunities, and suggesting profession-specific actions.

---

## 🚀 Features
- 📰 Fetches dynamic news (by profession + sector).  
- 💡 Translates news into career opportunities.  
- ⚡ Generates **daily micro-actions (≤15 min)**.  
- 🔗 Produces bilingual LinkedIn posts.  
- 🛠️ Suggests **3 mini-POC/portfolio ideas** daily.  
- 📈 Explains **compounding strategies** for career growth.  
- 🌐 Multi-language (English / Spanish).  
- Exposed via **FastAPI** endpoints.  

---

## 📂 Project Structure
- **agents/** → LangChain agent graphs (`daily_reader.py`)  
- **api/** → FastAPI app (`main.py`) + routes  
- **models/** → Pydantic schemas  
- **tests/** → Unit tests  
- `requirements.txt`, `Dockerfile`, `README.md`  

---

## 🛠️ Tech Stack
- **FastAPI** – API framework  
- **LangChain + LangGraph** – agent orchestration  
- **OpenAI / Local LLMs** – AI models  
- **Requests** – dynamic news fetching  
- **Pydantic** – input/output validation  
- **Docker** – containerized deployments  

---

## ⚡ Run Locally

1. Clone the repo
```bash
git clone https://github.com/mejorandro/growpulse-backend.git
cd growpulse-backend
