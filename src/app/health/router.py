"""
Health check endpoint for the UK Train Timetable API (v1).
Provides API status, server time, version, app metadata, and environment info.
"""
from fastapi import APIRouter, Response
from datetime import datetime
import platform
import sys
import os

from health import HealthResponse

router = APIRouter(prefix="/v1/health", tags=["health"])


@router.get(
    "/",
    summary="Health Check",
    description="Returns API status, server time, version, app metadata, and environment info.",
    status_code=200,
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    """
    Health check endpoint for API v1.
    Returns a HealthResponse object with status, current server time, API version, app name, description, Python version, OS info, and environment.
    """
    return HealthResponse(
        status="ok",
        time=datetime.now(datetime.timezone.utc)
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
