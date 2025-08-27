from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
from langchain_core.runnables import RunnableLambda

llm = ChatOpenAI(model="gpt-4o")

class State(TypedDict):
    task: str
    lang: str
    profession: str
    sector: str
    news: str
    meaning: str
    action: str
    linkedin_post: str
    poc_ideas: str
    compounding: str
    final_summary: str

def lang_prefix(lang: str, es: str, en: str):
    return es if lang == "es" else en

def news_agent(state: State) -> State:
    prompt = f"""{lang_prefix(state['lang'],
    "Sos un analista. Extraé 3–5 noticias recientes relacionadas a {state['profession']} en {state['sector']}.",
    "You are an analyst. Extract 3–5 recent news related to {state['profession']} in {state['sector']}.")}"""
    result = llm.invoke(prompt)
    state["news"] = result.content
    return state

# ... otros nodos igual (meaning_agent, action_agent, linkedin_agent, poc_agent, compounding_agent, final_summary)

builder = StateGraph(State)
builder.add_node("News", RunnableLambda(news_agent))
# ... añadir nodos ...
builder.set_entry_point("News")
# ... edges ...
builder.add_edge("Final", END)

graph = builder.compile(checkpointer=MemorySaver())

def run_pipeline(task: str, lang: str, profession: str, sector: str):
    result = graph.invoke({
        "task": task, "lang": lang, "profession": profession, "sector": sector
    })
    return result