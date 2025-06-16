import logging
from app.settings import settings

logger = logging.getLogger(__name__)


def test_settings_loaded():
    logger.info("Testing settings loaded.")
    assert hasattr(settings, "app_id")
    assert hasattr(settings, "app_key")
    assert hasattr(settings, "db_url")
    assert hasattr(settings, "env")
    assert settings.db_url.startswith("sqlite")
