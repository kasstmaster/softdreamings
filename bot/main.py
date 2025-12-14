from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands

from bot.core.logging_setup import setup_logging
from bot.core import settings
from bot.core import groups as groups_mod
from bot.core.db import init_pool, close_pool, run_migrations

# Transitional: legacy implementation registers all commands + tasks today
from bot import legacy_all_features as legacy

async def main() -> None:
    logger = setup_logging()
    if not settings.DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN (or TOKEN) env var")
    if not settings.DATABASE_URL:
        raise RuntimeError("Missing DATABASE_URL env var")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.logger = logging.getLogger("bot")  # type: ignore[attr-defined]

    # DB pool + migrations
    pool = await init_pool(settings.DATABASE_URL, ssl_mode=settings.DATABASE_SSL)
    await run_migrations(pool, Path(__file__).parent / "migrations")

    # Register shared groups first (so features can attach commands cleanly)
    for grp in groups_mod.ALL_GROUPS:
        try:
            bot.tree.add_command(grp)
        except Exception:
            # group may already exist if legacy added it; ignore
            logger.debug("Group already registered: %s", grp.name)

    # Register commands / listeners / tasks (legacy does this)
    legacy.setup(bot, pool, groups_mod)

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
        logger.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "unknown")

    # Start background loops (legacy)
    start = getattr(legacy, "start_background_tasks", None)
    if start:
        await start(bot, pool)

    try:
        await bot.start(settings.DISCORD_TOKEN)
    finally:
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())
