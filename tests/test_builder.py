from datetime import date

import httpx

from wall_tidbits.builder import apply_last_good, build_daily, worth_storing
from wall_tidbits.config import Settings

from .conftest import DATA

DAY = date(2026, 8, 25)


class FailingClient:
    async def get(self, url):
        raise httpx.ConnectError("down")


async def test_build_daily_tolerates_total_upstream_failure(tmp_path):
    settings = Settings(cache_dir=tmp_path, riddles_path=DATA / "riddles.json")
    from wall_tidbits.sources import load_riddles

    payload = await build_daily(DAY, settings, FailingClient(), load_riddles(settings.riddles_path))
    assert payload["word"] is None
    assert payload["history"] is None
    assert payload["fact"] is None
    assert payload["riddle"] is not None
    assert worth_storing(payload)


def test_apply_last_good_fills_missing_fields():
    payload = {"word": None, "history": {"year": 1900, "text": "kept"}, "fact": None, "riddle": {}}
    last_good = {
        "word": {"term": "old"},
        "history": {"year": 1, "text": "older"},
        "fact": {"text": "old fact?"},
    }
    merged = apply_last_good(payload, last_good)
    assert merged["word"] == {"term": "old"}
    assert merged["history"] == {"year": 1900, "text": "kept"}
    assert merged["fact"] == {"text": "old fact?"}
    assert merged["stale"] == ["word", "fact"]


def test_worth_storing_requires_any_content():
    empty = {"word": None, "history": None, "fact": None, "riddle": None}
    assert not worth_storing(empty)
    assert worth_storing({**empty, "riddle": {"question": "q"}})
