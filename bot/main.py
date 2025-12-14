from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from bot.core.logging_setup import setup_logging
from bot.core import settings
from bot.core import groups as groups_mod
from bot.core.db import init_pool, close_pool, run_migrations

# Transitional: legacy implementation defines `bot = commands.Bot(...)`
from bot import legacy_all_features as legacy


async def main() -> None:
    logger = setup_logging()

    if not settings.DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN (or TOKEN) env var")
    if not settings.DATABASE_URL:
        raise RuntimeError("Missing DATABASE_URL env var")

    # DB pool + migrations FIRST
    pool = await init_pool(settings.DATABASE_URL, ssl_mode=settings.DATABASE_SSL)
    await run_migrations(pool, Path(__file__).parent / "migrations")

    # Use the legacy bot instance (do NOT create a new Bot)
    bot = legacy.bot
    bot.logger = logging.getLogger("bot")  # optional, helpful for consistent logging

    # Give legacy access to the pool the legacy code expects
    legacy.db_pool = pool

    # Register shared groups (safe if legacy already added them)
    for grp in groups_mod.ALL_GROUPS:
        try:
            bot.tree.add_command(grp)
        except Exception:
            logger.debug("Group already registered: %s", grp.name)

    # Sync slash commands once on ready
    synced_flag = {"done": False}

    @bot.event
    async def on_ready():
        if synced_flag["done"]:
            return

        try:
            await bot.tree.sync()
            logger.info("Slash commands synced")
        except Exception:
            logger.exception("Slash command sync failed")

        synced_flag["done"] = True
        logger.info(
            "Logged in as %s (%s)",
            bot.user,
            bot.user.id if bot.user else "unknown",
        )

    # Start background loops (legacy) if exposed
    start = getattr(legacy, "start_background_tasks", None)
    if start:
        try:
            await start(bot, pool)
        except Exception:
            logger.exception("Failed to start background tasks")

    try:
        await bot.start(settings.DISCORD_TOKEN)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
