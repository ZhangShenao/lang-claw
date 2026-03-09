import logging

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=logging.INFO if settings.app_env != "development" else logging.DEBUG,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
