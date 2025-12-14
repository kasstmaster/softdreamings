"""plague feature module.

Transitional wrapper: delegates to legacy_all_features.
You can later move real implementations into this module.
"""

from __future__ import annotations
from typing import Any
from bot import legacy_all_features as legacy

def setup(bot: Any, db_pool: Any, groups: Any) -> None:
    # legacy registers everything; keep for interface consistency
    return legacy.setup(bot, db_pool, groups)

async def start_tasks(bot: Any, db_pool: Any) -> None:
    # legacy starts background loops if defined
    start = getattr(legacy, "start_background_tasks", None)
    if start:
        await start(bot, db_pool)
