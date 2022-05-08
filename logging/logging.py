from app_config import LOG_LEVEL
from logging.logging_constants import INFO_LEVEL, LOG_LEVEL_TO_ENABLED_LEVELS


def log(message, level=INFO_LEVEL, **kwargs):
    """Print message if log level is turned on in app_config."""
    if level in LOG_LEVEL_TO_ENABLED_LEVELS[LOG_LEVEL]:
        print(f"[{level}]\n{message}", **kwargs)
