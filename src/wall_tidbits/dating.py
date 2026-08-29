from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def now_in(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def today_in(tz_name: str) -> date:
    return now_in(tz_name).date()


def parse_date(value: str | None, tz_name: str) -> date:
    if not value:
        return today_in(tz_name)
    return date.fromisoformat(value)


def next_refresh_at(tz_name: str, hour: int = 0, minute: int = 5) -> datetime:
    now = now_in(tz_name)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target
