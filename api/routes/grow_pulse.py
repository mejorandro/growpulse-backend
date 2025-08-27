from fastapi import APIRouter
from pydantic import BaseModel
from agents.grow_pulse import run_pipeline

router = APIRouter()

class GrowPulseInput(BaseModel):
    task: str = "Daily briefing"
    lang: str = "en"
    profession: str = "Developer"
    sector: str = "AI"

class GrowPulseOutput(BaseModel):
    news: str
    meaning: str
    action: str
    linkedin_post: str
    poc_ideas: str
    compounding: str
    final_summary: str

@router.post("/", response_model=GrowPulseOutput)
def grow_pulse(input: GrowPulseInput):
    result = run_pipeline(input.task, input.lang, input.profession, input.sector)
    return GrowPulseOutput(**result)