"""
Production-grade health check endpoint for the UK Train Timetable API (v1).
Provides API status, server time, version, app metadata, and environment info.
Follows best practices for logging, error handling, and OpenAPI documentation.
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
    description="""
    Returns API status, server time, version, app metadata, and environment info.
    - **status**: API status (ok/error)
    - **time**: Current server time in ISO 8601 UTC
    - **api_version**: API version string
    - **app_name**: Application name
    - **description**: Endpoint description
    - **python_version**: Python version
    - **os**: Operating system
    - **os_version**: OS version
    - **server**: Hostname
    - **author**: Author info
    - **env**: Environment (DEV/PROD/etc)
    """,
    status_code=200,
    response_model=HealthResponse,
    tags=["health"],
)
def health_check() -> HealthResponse:
    """
    Production-grade health check endpoint for API v1.
    Returns a HealthResponse object with status, current server time, API version,
    app name, description, Python version, OS info, and environment.
    Logs request and response for observability. Raises and logs errors if any occur.
    """
    logger.info("Health check endpoint called.")
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
    except Exception as exc:
        logger.exception("Health check failed.")
        raise
