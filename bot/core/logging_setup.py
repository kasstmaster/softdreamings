import logging
import os
import sys

def setup_logging() -> logging.Logger:
    """Configure root logger for Railway (stdout) + local dev."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # Quiet noisy libs a bit
    logging.getLogger("discord").setLevel(os.getenv("DISCORD_LOG_LEVEL", "WARNING").upper())
    logging.getLogger("asyncio").setLevel(os.getenv("ASYNCIO_LOG_LEVEL", "WARNING").upper())
    return logging.getLogger("bot")
