"""Structured logging setup using loguru."""

import sys

from loguru import logger

from src.core.config import settings


def setup_logging() -> None:
    """Configure loguru with colorized console output."""
    logger.remove()
    level = "DEBUG" if settings.DEBUG else "INFO"

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(sys.stderr, format=fmt, level=level, enqueue=True)
    logger.info(f"Logging initialized | level={level} debug={settings.DEBUG}")
