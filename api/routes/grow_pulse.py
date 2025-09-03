from fastapi import APIRouter
from pydantic import BaseModel
from agents.grow_pulse import run_blog_body_pipeline, run_blog_intro_pipeline

router = APIRouter()

class GrowPulseInput(BaseModel):
    task: str = "Daily briefing"
    lang: str = "en"
    profession: str = "Developer"
    sector: str = "AI"

class GrowPulseBlogBodyOutput(BaseModel):
    news: str
    meaning: str
    action: str
    linkedin_post: str
    poc_ideas: str
    compounding: str
    final_summary: str

class GrowPulseBlogIntroOutput(BaseModel):
    title: str
    summary: str

@router.post("/", response_model=GrowPulseBlogBodyOutput)
def grow_pulse(input: GrowPulseInput):
    result = run_blog_body_pipeline(input.task, input.lang, input.profession, input.sector)
    return GrowPulseBlogBodyOutput(**result)

@router.post("/blog-intro", response_model=GrowPulseBlogIntroOutput)
def grow_pulse_title(input: GrowPulseInput):
    result = run_blog_intro_pipeline(input.task, input.lang, input.profession, input.sector)
    return GrowPulseBlogIntroOutput(**result)