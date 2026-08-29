from datetime import date

from wall_tidbits.normalize import budget, family_safe, stable_index, tidy_ws

API_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/{month}/{day}"

MIN_LEN = 60
MAX_LEN = 230
RELAXED_MAX_LEN = 260


def onthisday_url(day: date) -> str:
    return API_URL.format(month=day.strftime("%m"), day=day.strftime("%d"))


async def fetch_on_this_day(client, day: date, family: bool = True) -> dict | None:
    resp = await client.get(onthisday_url(day))
    resp.raise_for_status()
    return parse_onthisday(resp.json(), day, family)


def parse_onthisday(payload: dict, day: date, family: bool = True) -> dict | None:
    items = payload.get("selected") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    candidates = _candidates(items, family)
    if not candidates:
        candidates = _candidates(items, family=False)
    if not candidates:
        candidates = [_as_record(item) for item in items if _as_record(item)]
    if not candidates:
        return None
    chosen = candidates[stable_index(day.isoformat(), len(candidates))]
    return {
        "year": chosen["year"],
        "text": budget(chosen["text"], MAX_LEN),
        "source": "Wikipedia",
        "source_url": chosen["source_url"] or onthisday_url(day),
        "license": "CC BY-SA 4.0",
    }


def _candidates(items: list[object], family: bool) -> list[dict]:
    out = []
    for item in items:
        record = _as_record(item)
        if record is None:
            continue
        if not (MIN_LEN <= len(record["text"]) <= MAX_LEN):
            continue
        if family and not family_safe(record["text"]):
            continue
        out.append(record)
    return out


def _as_record(item: object) -> dict | None:
    if not isinstance(item, dict):
        return None
    text = tidy_ws(str(item.get("text") or ""))
    if not text or len(text) > RELAXED_MAX_LEN:
        return None
    pages = item.get("pages") or []
    source_url = ""
    if pages:
        try:
            source_url = pages[0]["content_urls"]["desktop"]["page"]
        except (KeyError, TypeError):
            source_url = ""
    return {"year": item.get("year"), "text": text, "source_url": source_url}
