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

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY no está definido.")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

class State(TypedDict):
    task: str
    lang: str            # "es" | "en"
    profession: str      # NUEVO
    sector: str          # NUEVO
    news: str
    meaning: str
    action: str
    linkedin_post: str
    poc_ideas: str
    compounding: str
    final_summary: str

llm = ChatOpenAI(model=OPENAI_MODEL)

def format_instruction(lang: str) -> str:
    return (
        "No saludes al usuario ni incluyas frases de cortesía. "
        "Si hay un texto introductorio agrega un salto de línea extra después de él para separarlo claramente del contenido principal. "
        "No agregues encabezados ni etiquetas de sección, solo empieza directamente con el texto o contenido que fuiste creado para generar. "
        "Usa saltos de línea reales (presiona Enter dos veces) para separar párrafos y también al final. "
        "No escribas '\\n\\n' como texto literal, deben ser saltos de línea reales. "
        "El resultado debe estar listo para pasar a un parser de Markdown y verse correctamente espaciado verticalmente."
        if lang == "es"
        else
        "Do not greet the user or include courtesy phrases. "
        "If there is an introductory text, add an extra line break after it to clearly separate it from the main content. "
        "Do not add headings or section labels, just start directly with the text or content you were created to generate. "
        "Use real line breaks (press Enter twice) to separate paragraphs and also at the end. "
        "Do not output '\\n\\n' as literal text, they must be real line breaks. "
        "The output must be ready to be parsed as Markdown and look properly spaced vertically."
    )



def lang_prefix(lang: str, es: str, en: str) -> str:
    return es if lang == "es" else en
    

def _ctx(state: State) -> str:
    # Contexto común para todos los prompts
    prof = state.get("profession", "") or ""
    sect = state.get("sector", "") or ""
    task = state.get("task", "") or ""
    return f"Profession: {prof}\nSector: {sect}\nTask: {task}\n"

def news_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un analista de IA. Extraé 3–5 noticias recientes de IA (OpenAI, Anthropic, DeepMind, open-source, enterprise). Sé concreto, sin inventar.",
    "You are an AI analyst. Extract 3–5 recent AI news (OpenAI, Anthropic, DeepMind, open-source, enterprise). Be concrete, no fabrication.")}

{_ctx(state)}
{format_instruction(state['lang'])}
"""
    result = llm.invoke(prompt)
    state["news"] = result.content
    return state

def meaning_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un coach de carrera para un Tech Lead .NET + AWS + agentes LLM. Explicá cómo cada noticia es oportunidad real en banca, seguros, salud, travel, energía.",
    "You are a career coach for a .NET + AWS + LLM-agents Tech Lead. Explain how each news becomes real opportunities in finance, insurance, healthcare, travel, energy.")}

{_ctx(state)}
Noticias:
{state['news']}
{format_instruction(state['lang'])}
"""
    result = llm.invoke(prompt)
    state["meaning"] = result.content
    return state

def action_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Proponé UNA micro-acción (≤15 min) ejecutable hoy (post corto, DM, pitch, probar repo), alineada al contexto.",
    "Suggest ONE micro-action (≤15 min) executable today (short post, DM, pitch, test repo), aligned to the context.")}

{_ctx(state)}
{format_instruction(state['lang'])}
"""
    result = llm.invoke(prompt)
    state["action"] = result.content
    return state

def linkedin_agent(state: State) -> State:
    prompt = f"""Generate 2 LinkedIn posts ({lang_prefix(state['lang'], "uno en español y uno en inglés", "one in English and one in Spanish")}),
style: authoritative, inspiring, not egocentric. Goal: attract inbound high-value leads (+10K/month).

{_ctx(state)}
{format_instruction(state['lang'])}
News:
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
    "Generá 3 POCs simples (≤45 min) conectados a las noticias y contexto (profesión/sector).",
    "Generate 3 simple POCs (≤45 min) tied to the news and context (profession/sector).")}

{_ctx(state)}
{format_instruction(state['lang'])}
News:
{state['news']}
"""
    result = llm.invoke(prompt)
    state["poc_ideas"] = result.content
    return state

def compounding_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Explicá cómo post, acción y POCs se acumulan estratégicamente a oportunidades globales (+10K/mes).",
    "Explain how post, action, and POCs strategically compound toward global opportunities (+10K/month).")}

{_ctx(state)}
{format_instruction(state['lang'])}
Action:
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

{_ctx(state)}
{format_instruction(state['lang'])}
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

builder = StateGraph(State)
builder.add_node("News", RunnableLambda(news_agent))
builder.add_node("Meaning", RunnableLambda(meaning_agent))
builder.add_node("Action", RunnableLambda(action_agent))
builder.add_node("LinkedIn", RunnableLambda(linkedin_agent))
builder.add_node("POCs", RunnableLambda(poc_agent))
builder.add_node("Compounding", RunnableLambda(compounding_agent))
builder.add_node("Final", RunnableLambda(final_summary))

builder.add_edge(START, "News")
builder.add_edge("News", "Meaning")
builder.add_edge("Meaning", "Action")
builder.add_edge("Action", "LinkedIn")
builder.add_edge("LinkedIn", "POCs")
builder.add_edge("POCs", "Compounding")
builder.add_edge("Compounding", "Final")
builder.add_edge("Final", END)

graph = builder.compile(checkpointer=MemorySaver())

def run_pipeline(task: str, lang: str = "es", profession: str | None = None, sector: str | None = None) -> dict:
    state_in: State = {
        "task": task or "",
        "lang": lang or "es",
        "profession": (profession or "").strip(),
        "sector": (sector or "").strip(),
        "news": "", "meaning": "", "action": "",
        "linkedin_post": "", "poc_ideas": "", "compounding": "", "final_summary": ""
    }
    result: State = graph.invoke(state_in, config={"configurable": {"thread_id": "growpulse-api"}})
    return {
        "news": result.get("news", ""),
        "meaning": result.get("meaning", ""),
        "action": result.get("action", ""),
        "linkedin_post": result.get("linkedin_post", ""),
        "poc_ideas": result.get("poc_ideas", ""),
        "compounding": result.get("compounding", ""),
        "final_summary": result.get("final_summary", ""),
    }
