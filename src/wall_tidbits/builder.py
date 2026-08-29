import asyncio
from datetime import UTC, date, datetime

from wall_tidbits.config import Settings
from wall_tidbits.sources import (
    fetch_fact_of_the_day,
    fetch_on_this_day,
    fetch_word_of_the_day,
    pick_riddle,
)

CONTENT_FIELDS = ("word", "history", "fact", "riddle")
FALLBACK_FIELDS = ("word", "history", "fact")


async def _safe(coro):
    try:
        return await coro
    except Exception:
        return None


async def build_daily(day: date, settings: Settings, client, riddles: list[dict]) -> dict:
    family = settings.family_filter_enabled()
    word, history, fact = await asyncio.gather(
        _safe(fetch_word_of_the_day(client, day)),
        _safe(fetch_on_this_day(client, day, family)),
        _safe(fetch_fact_of_the_day(client, day, family)),
    )
    return {
        "date": day.isoformat(),
        "timezone": settings.timezone,
        "generated_at": datetime.now(UTC).isoformat(),
        "word": word,
        "history": history,
        "fact": fact,
        "riddle": pick_riddle(riddles, day, settings.riddle_seed),
        "stale": [],
    }


def apply_last_good(payload: dict, last_good: dict | None) -> dict:
    if not last_good:
        return payload
    stale = []
    for field in FALLBACK_FIELDS:
        if not payload.get(field) and last_good.get(field):
            payload[field] = last_good[field]
            stale.append(field)
    payload["stale"] = stale
    return payload


def worth_storing(payload: dict) -> bool:
    return any(payload.get(field) for field in CONTENT_FIELDS)
