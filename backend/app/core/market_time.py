from datetime import datetime, time
from zoneinfo import ZoneInfo


NY_TZ = ZoneInfo("America/New_York")


def to_market_time(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")
    return ts.astimezone(NY_TZ)


def market_time_only(ts: datetime) -> time:
    return to_market_time(ts).time()


def market_date(ts: datetime):
    return to_market_time(ts).date()


def is_regular_market_session(ts: datetime) -> bool:
    mt = market_time_only(ts)
    return time(9, 30) <= mt < time(16, 0)