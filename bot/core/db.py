from __future__ import annotations

import asyncpg
import logging
import os
from pathlib import Path
from typing import Optional, Sequence

logger = logging.getLogger("bot.db")

_pool: Optional[asyncpg.pool.Pool] = None

async def init_pool(dsn: str, *, ssl_mode: str = "") -> asyncpg.pool.Pool:
    global _pool
    if _pool:
        return _pool
    ssl = None
    if ssl_mode == "require":
        # asyncpg accepts ssl=True / ssl="require" in newer versions; ssl=True works broadly.
        ssl = True
    _pool = await asyncpg.create_pool(dsn, ssl=ssl, min_size=1, max_size=int(os.getenv("DB_POOL_MAX", "5")))
    logger.info("DB pool initialized")
    return _pool

async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("DB pool closed")

async def run_migrations(pool: asyncpg.pool.Pool, migrations_dir: Path) -> None:
    """Run .sql migrations in order, tracking in schema_migrations."""
    migrations_dir = Path(migrations_dir)
    if not migrations_dir.exists():
        logger.warning("Migrations dir does not exist: %s", migrations_dir)
        return

    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        applied = {r["filename"] for r in await conn.fetch("SELECT filename FROM schema_migrations;")}

        files = sorted([p for p in migrations_dir.glob("*.sql")])
        for f in files:
            if f.name in applied:
                continue
            sql = f.read_text(encoding="utf-8")
            logger.info("Applying migration: %s", f.name)
            try:
                await conn.execute(sql)
                await conn.execute("INSERT INTO schema_migrations(filename) VALUES($1);", f.name)
            except Exception:
                logger.exception("Migration failed: %s", f.name)
                raise

    logger.info("Migrations complete (%d files)", len(list(migrations_dir.glob("*.sql"))))
