"""
Provides API Server status, server time, version, app metadata, and environment info.
"""

import logging
import os
import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter

from app.health.schema import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    summary="Health Check",
    description="Returns API status" "",
    status_code=200,
    response_model=HealthResponse,
    tags=["health"],
)
def health_check() -> HealthResponse:
    """
    Health check endpoint to provide API server status, current time, version,
    """
    try:
        resp = HealthResponse(
            status="ok",
            time=datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            api_version="v1",
            app_name="UK Train Timetable",
            description="Health check endpoint for the UK Train Timetable API.",
            python_version=sys.version.split()[0],
            os=platform.system(),
            os_version=platform.version(),
            server=platform.node(),
            author="Rajath Rao Web_soltZ <rajathn8@gmail.com>",
            env=os.getenv("APP_ENV", "DEV"),
        )
        logger.debug(f"HealthResponse: {resp}")
        return resp
    except Exception:
        logger.exception("Health check failed.")
        raise
