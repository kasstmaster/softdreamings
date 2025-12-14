from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

def now_in_tz(tz_name: str) -> dt.datetime:
    return dt.datetime.now(tz=ZoneInfo(tz_name))

def today_in_tz(tz_name: str) -> dt.date:
    return now_in_tz(tz_name).date()
