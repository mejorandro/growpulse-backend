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

OPENAI_MODEL_FAST = os.getenv("OPENAI_MODEL_FAST", "gpt-4o-mini")
OPENAI_MODEL_HEAVY = os.getenv("OPENAI_MODEL_HEAVY", "gpt-4o")


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

llm_fast = ChatOpenAI(model=OPENAI_MODEL_FAST)
llm_heavy = ChatOpenAI(model=OPENAI_MODEL_HEAVY)

def format_instruction(lang: str) -> str:
    return (
         "Esta información se renderizara luego en Formato Markdown. "
        "No saludes al usuario ni incluyas frases de cortesía. "
        "Si hay un texto introductorio agrega un salto de línea extra después de él para separarlo claramente del contenido principal. "
        "No agregues encabezados ni etiquetas de sección, solo empieza directamente con el texto o contenido que fuiste creado para generar. "
        "Usa saltos de línea reales (presiona Enter dos veces) para separar párrafos y también al final. "
        "No escribas '\\n\\n' como texto literal, deben ser saltos de línea reales. "
        "El resultado debe estar listo para pasar a un parser de Markdown y verse correctamente espaciado verticalmente."
        "No Emojis"
        if lang == "es"
        else
        "Do not greet the user or include courtesy phrases. "
        "If there is an introductory text, add an extra line break after it to clearly separate it from the main content. "
        "Do not add headings or section labels, just start directly with the text or content you were created to generate. "
        "Use real line breaks (press Enter twice) to separate paragraphs and also at the end. "
        "Do not output '\\n\\n' as literal text, they must be real line breaks. "
        "The output must be ready to be parsed as Markdown and look properly spaced vertically."
        "No emojis"
    )



def lang_prefix(lang: str, es: str, en: str) -> str:
    return es if lang == "es" else en
    

def _ctx(state: State) -> str:
    # Contexto común para todos los prompts
    prof = state.get("profession", "") or ""
    sect = state.get("sector", "") or ""
    task = state.get("task", "") or ""
    return f"Profession: {prof}\nSector: {sect}\nTask: {task}\n"



def generate_title(task: str, lang: str = "es", profession: str | None = None, sector: str | None = None) -> str:
    prompt = f"""{lang_prefix(lang,
    "Generá un título breve, impactante y llamativo (máx. 10 palabras) que resuma la esencia del briefing diario. El resultado debe estar listo para pasar a un parser de Markdown y verse correctamente. Sin emojis, sin saltos de linea, ni simbolos, solo texto puro. Evita agregar comillas o cualquier simbolo!. Debes sonar directo, aspiracional y enfocado en resultados. ",
    "Generate a short, catchy, and engaging title (max. 10 words) that captures the essence of today's daily briefing. The output must be ready to be parsed as Markdown and look properly. No emojis, no break lines, just pure text. Avoid adding quotes or any other symbol. Be direct, aspirational, and results-focused.")}

    Profession: {profession or ""}
    Sector: {sector or ""}
    Task: {task or ""}

    """
    result = llm_fast.invoke(prompt)
    return result.content.strip()

def generate_blog_summary(
    task: str,
    lang: str = "es",
    profession: str | None = None,
    sector: str | None = None
) -> str:
    """
    Generate an impactful summary/intro paragraph for the GrowPulse blog.
    - Acts as a 'hook' before the full blog body.
    - Mix of value explanation + curiosity builder.
    - Uses profession and sector as context, but lets the AI phrase them naturally.
    """

    # Context block (not injected literally into sentences)
    context = f"Profession: {profession or ''}\nSector: {sector or ''}\nTask: {task or ''}\n"

    base_prompt = lang_prefix(
        lang,
        # --- Spanish version ---
        "Escribí un párrafo breve e impactante (3–4 frases) que explique:\n"
        "- Por qué este briefing diario (GrowPulse) es valioso para el lector.\n"
        "- Cómo conecta con su contexto profesional y sector.\n"
        "- Cómo lo que estamos construyendo (Agentes de IA, insights prácticos) puede ayudarlo a crecer, innovar o captar oportunidades.\n"
        "El tono debe ser motivador, claro y generar expectativa. Terminá con una idea que invite a seguir leyendo el cuerpo del blog.",
        # --- English version ---
        "Write a short, impactful paragraph (3–4 sentences) that explains:\n"
        "- Why this daily briefing (GrowPulse) is valuable for the reader.\n"
        "- How it connects with their professional context and sector.\n"
        "- How what we are building (AI Agents, practical insights) can help them grow, innovate, or capture opportunities.\n"
        "Tone should be motivating, clear, and create anticipation. End with a line that makes the reader curious to continue with the blog body."
    )

    prompt = f"""{base_prompt}

{context}
{format_instruction(lang)}
"""

    result = llm_fast.invoke(prompt)
    return result.content.strip()

def news_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un analista de IA. Extraé 3–5 noticias recientes de IA (OpenAI, Anthropic, DeepMind, open-source, enterprise). Sé concreto, sin inventar. bullets de 1 línea cada una, con foco en impacto práctico. No redactes como artículo periodístico, sino como inteligencia ejecutiva.",
    "You are an AI analyst. Extract 3–5 recent AI news (OpenAI, Anthropic, DeepMind, open-source, enterprise). Be concrete, no fabrication. 1-line bullets, focused on practical impact. Do not write like a news article, write like executive intelligence.")}

{_ctx(state)}
{format_instruction(state['lang'])}
"""
    result = llm_fast.invoke(prompt)
    state["news"] = result.content
    return state

def meaning_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un coach de carrera para un Tech Lead .NET + AWS + agentes LLM. Explicá cómo cada noticia es oportunidad real en banca, seguros, salud, travel, energía. 1–2 frases por noticia.",
    "You are a career coach for a .NET + AWS + LLM-agents Tech Lead. Explain how each news becomes real opportunities in finance, insurance, healthcare, travel, energy. 1–2 sentences per news.")}

{_ctx(state)}
Noticias:
{state['news']}
{format_instruction(state['lang'])}
"""
    result = llm_fast.invoke(prompt)
    state["meaning"] = result.content
    return state

def action_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Proponé UNA micro-acción (≤15 min) ejecutable hoy (post corto, DM, pitch, probar repo), alineada al contexto. Responde en una sola línea, empezando con un verbo imperativo.",
    "Suggest ONE micro-action (≤15 min) executable today (short post, DM, pitch, test repo), aligned to the context. Respond in a single line, starting with an imperative verb.")}

{_ctx(state)}
{format_instruction(state['lang'])}
"""
    result = llm_fast.invoke(prompt)
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
    result = llm_fast.invoke(prompt)
    state["linkedin_post"] = result.content
    return state

def poc_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Generá 3 POCs simples (≤45 min) conectados a las noticias y contexto (profesión/sector). Formato bullet: Idea (≤10 palabras) + Beneficio (1 frase) + Tiempo estimado. Los POCs deben conectar con las noticias y el contexto profesional/sector.",
    "Generate 3 simple POCs (≤45 min) tied to the news and context (profession/sector). Bullet format: Idea (≤10 words) + Benefit (1 sentence) + Estimated time. POCs must connect with the news and professional/sector context.")}

{_ctx(state)}
{format_instruction(state['lang'])}
News:
{state['news']}
"""
    result = llm_fast.invoke(prompt)
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
    result = llm_heavy.invoke(prompt)
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
    result = llm_heavy.invoke(prompt)
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

def run_blog_body_pipeline(task: str, lang: str = "es", profession: str | None = None, sector: str | None = None) -> dict:
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


def run_blog_intro_pipeline(task: str, lang: str = "es", profession: str | None = None, sector: str | None = None) -> dict:
   
    state_in: State = {
        "task": task or "",
        "lang": lang or "es",
        "profession": (profession or "").strip(),
        "sector": (sector or "").strip(),
        # intro-specific fields
        "title": "",
        "summary": "",
    }

    # --- Call the intro agent ---
    title = generate_title(
        state_in["task"],
        state_in["lang"],
        state_in["profession"],
        state_in["sector"],
    )

    summary = generate_blog_summary(
        state_in["task"],
        state_in["lang"],
        state_in["profession"],
        state_in["sector"],
    )

    # --- Return clean result ---
    return {
        "title": title,
        "summary": summary
    }