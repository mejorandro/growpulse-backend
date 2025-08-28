# agents/grow_pulse.py
from __future__ import annotations

import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# --- Cargar variables de entorno (.env en la raíz del repo) ---
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Validación temprana para evitar errores silenciosos
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY no está definido. Asegúrate de que .env exista en la raíz "
        "y que Uvicorn se ejecute con ese cwd o usa --env-file .env."
    )

# Modelo configurable vía env (opcional)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# --- Definición del estado global del grafo ---
class State(TypedDict):
    task: str
    lang: str            # "es" o "en"
    news: str
    meaning: str
    action: str
    linkedin_post: str
    poc_ideas: str
    compounding: str
    final_summary: str

# --- LLM (instanciado después de load_dotenv) ---
llm = ChatOpenAI(model=OPENAI_MODEL)

# --- Helper de idioma ---
def lang_prefix(lang: str, es: str, en: str) -> str:
    return es if lang == "es" else en

# --- Nodos (agentes) ---
def news_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un analista de IA. Extraé las 3–5 noticias más recientes sobre IA (OpenAI, Anthropic, DeepMind, open-source, enterprise). Redactá en lenguaje claro y útil, sin inventar.",
    "You are an AI analyst. Extract 3–5 of the most recent AI news (OpenAI, Anthropic, DeepMind, open-source, enterprise adoption). Write clearly and practically, no fabrication.")}

Task: {state['task']}
"""
    result = llm.invoke(prompt)
    state["news"] = result.content
    return state

def meaning_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un coach de carrera para un Tech Lead .NET + AWS + constructor de agentes LLM. Explicá cómo cada noticia representa una oportunidad real en banca, seguros, salud, travel, energía.",
    "You are a career coach for a Tech Lead (.NET + AWS + LLM agents). Explain how each news item becomes real opportunities in finance, insurance, healthcare, travel, and energy.")}

Noticias:
{state['news']}
"""
    result = llm.invoke(prompt)
    state["meaning"] = result.content
    return state

def action_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Proponé UNA micro-acción diaria (≤15 min) que acerque al usuario a oportunidades globales. Debe ser concreta y ejecutable hoy (ej.: post corto en LinkedIn, DM, pitch, probar repo).",
    "Suggest ONE micro-action (≤15 min) that brings the user closer to global opportunities. Must be concrete and executable today (e.g., short LinkedIn post, DM, pitch snippet, test a repo).")}"""
    result = llm.invoke(prompt)
    state["action"] = result.content
    return state

def linkedin_agent(state: State) -> State:
    prompt = f"""Generate 2 LinkedIn posts ({lang_prefix(state['lang'], "uno en español y uno en inglés", "one in English and one in Spanish")}),
style: authoritative, inspiring, not egocentric. Goal: attract inbound high-value leads (+10K/month, no micromanagement).

Context:
{state['news']}
Meaning:
{state['meaning']}
Daily Action:
{state['action']}
"""
    result = llm.invoke(prompt)
    state["linkedin_post"] = result.content
    return state

def poc_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Generá 3 ideas de POC simples (45 min) conectadas a las noticias. Ej: .NET API + LLM, middleware de seguridad, extractor de facturas, workflow agent.",
    "Generate 3 simple POC ideas (45 min) connected to the news. Ex: .NET API + LLM, safety middleware, invoice extractor, workflow agent.")}

Noticias:
{state['news']}
"""
    result = llm.invoke(prompt)
    state["poc_ideas"] = result.content
    return state

def compounding_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Explicá cómo el post, la acción y los POCs se acumulan estratégicamente hacia oportunidades globales de consultoría (+10K/mes).",
    "Explain how the LinkedIn post, action, and POCs strategically compound toward global consulting opportunities (+10K/month).")}

Acción:
{state['action']}
Post:
{state['linkedin_post']}
POCs:
{state['poc_ideas']}
"""
    result = llm.invoke(prompt)
    state["compounding"] = result.content
    return state

def final_summary(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "📋 Resumen Final de la Lectura de Hoy",
    "📋 Final Summary of Today's Reading")}

📰 Noticias:
{state['news']}

💡 Oportunidades:
{state['meaning']}

⚡ Acción diaria:
{state['action']}

🔗 Post LinkedIn:
{state['linkedin_post']}

🛠️ POCs:
{state['poc_ideas']}

📈 Compounding:
{state['compounding']}
"""
    result = llm.invoke(prompt)
    state["final_summary"] = result.content
    return state

# --- Construcción del grafo ---
builder = StateGraph(State)

# 1) Registrar TODOS los nodos primero
builder.add_node("News", RunnableLambda(news_agent))
builder.add_node("Meaning", RunnableLambda(meaning_agent))
builder.add_node("Action", RunnableLambda(action_agent))
builder.add_node("LinkedIn", RunnableLambda(linkedin_agent))
builder.add_node("POCs", RunnableLambda(poc_agent))
builder.add_node("Compounding", RunnableLambda(compounding_agent))
builder.add_node("Final", RunnableLambda(final_summary))

# 2) Definir edges DESPUÉS de registrar nodos
builder.add_edge(START, "News")
builder.add_edge("News", "Meaning")
builder.add_edge("Meaning", "Action")
builder.add_edge("Action", "LinkedIn")
builder.add_edge("LinkedIn", "POCs")
builder.add_edge("POCs", "Compounding")
builder.add_edge("Compounding", "Final")
builder.add_edge("Final", END)

# 3) Compilar con checkpoint en memoria (para threads por request)
graph = builder.compile(checkpointer=MemorySaver())

# --- API de uso desde FastAPI ---
def run_pipeline(task: str, lang: str = "es") -> dict:
    """
    Ejecuta el grafo y devuelve un diccionario serializable.
    """
    state_in: State = {"task": task or "", "lang": lang or "es",
                       "news": "", "meaning": "", "action": "",
                       "linkedin_post": "", "poc_ideas": "", "compounding": "", "final_summary": ""}

    result: State = graph.invoke(
        state_in,
        config={"configurable": {"thread_id": "growpulse-api"}}
    )

    # Devuelve solo las claves relevantes (ordenadas)
    return {
        "news": result.get("news", ""),
        "meaning": result.get("meaning", ""),
        "action": result.get("action", ""),
        "linkedin_post": result.get("linkedin_post", ""),
        "poc_ideas": result.get("poc_ideas", ""),
        "compounding": result.get("compounding", ""),
        "final_summary": result.get("final_summary", ""),
    }

# --- Self-check opcional (ejecutar: python -m agents.grow_pulse) ---
if __name__ == "__main__":
    out = run_pipeline("Foco en enterprise AI & seguridad", "es")
    print("\n=== NEWS ===\n", out["news"])
    print("\n=== MEANING ===\n", out["meaning"])
    print("\n=== ACTION ===\n", out["action"])
    print("\n=== LINKEDIN ===\n", out["linkedin_post"])
    print("\n=== POCs ===\n", out["poc_ideas"])
    print("\n=== COMPOUNDING ===\n", out["compounding"])
    print("\n=== FINAL ===\n", out["final_summary"])
