import logging

from fastapi import FastAPI

from app.health.router import router as health_router
from app.uk_train_schedule.router import router as journey_router

logger = logging.getLogger(__name__)
app = FastAPI(title="UK Train Timetable API")
logger.info("FastAPI app instance created.")
app.include_router(health_router)
logger.info("Health router included.")
app.include_router(journey_router)
logger.info("Journey router included.")


@app.get("/", include_in_schema=False)
def root():
    return {
        "status": "ok",
        "message": "UK Train Timetable API. See /health for health check.",
    }
