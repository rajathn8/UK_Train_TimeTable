import logging

from fastapi import FastAPI

from .health.router import router as health_router
from .uk_train_schedule.router import router as journey_router

logger = logging.getLogger(__name__)
app = FastAPI(title="UK Train Timetable API")
logger.info("FastAPI app instance created.")
app.include_router(health_router)
logger.info("Health router included.")
app.include_router(journey_router)
logger.info("Journey router included.")


@app.get("/", include_in_schema=False)
def root():
    logger.info("Root endpoint called.")
    try:
        resp = {
            "status": "ok",
            "message": "UK Train Timetable API. See /health for health check.",
        }
        logger.debug(f"Root response: {resp}")
        return resp
    except Exception as e:
        logger.error(f"Root endpoint failed: {e}")
        raise
