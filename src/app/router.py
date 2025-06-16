import logging

from fastapi import FastAPI

from .health.router import router as health_router
from .uk_train_schedule.router import router as journey_router

logger = logging.getLogger(__name__)

app = FastAPI(title="UK Train Timetable API")

app.include_router(health_router)
app.include_router(journey_router)


@app.get("/", include_in_schema=False)
def root():
    logger.info("Root endpoint called.")
    return {
        "status": "ok",
        "message": "UK Train Timetable API. See /health for health check.",
    }
