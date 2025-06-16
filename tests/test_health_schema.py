from app.health.schema import HealthResponse
import logging

logger = logging.getLogger(__name__)


def test_health_response_fields():
    logger.info("Testing HealthResponse fields.")
    resp = HealthResponse(
        status="ok",
        time="2025-06-16T10:00:00Z",
        api_version="v1",
        app_name="UK Train Timetable",
        description="desc",
        python_version="3.12.0",
        os="macOS",
        os_version="1.0",
        server="localhost",
        author="test",
        env="DEV",
    )
    assert resp.status == "ok"
    assert resp.env == "DEV"
    assert resp.api_version == "v1"
