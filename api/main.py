from fastapi import FastAPI
from api.routes import grow_pulse

app = FastAPI(
    title="Grow-Pulse API",
    description="Daily Reader dinámico, subproducto de GrowRoutine"
)

app.include_router(grow_pulse.router, prefix="/grow-pulse", tags=["Grow-Pulse"])
