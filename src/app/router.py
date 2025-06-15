from fastapi import FastAPI

from .health.router import router as health_router
from .uk_train_schedule.router import router as journey_router

app = FastAPI(title="UK Train Timetable API")

app.include_router(health_router)
app.include_router(journey_router)


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok", "message": "UK Train Timetable API. See /v1/health for health check."}
