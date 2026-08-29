from datetime import date, timedelta

from wall_tidbits.cache import DailyCache


def test_store_and_load_roundtrip(tmp_path):
    cache = DailyCache(tmp_path)
    day = date(2026, 8, 25)
    payload = {"date": day.isoformat(), "word": {"term": "demake"}}
    cache.store(day, payload)
    assert cache.load(day) == payload
    assert cache.load_last_good() == payload


def test_load_missing_returns_none(tmp_path):
    cache = DailyCache(tmp_path)
    assert cache.load(date(2026, 8, 25)) is None
    assert cache.load_last_good() is None


def test_prune_removes_old_days_but_keeps_recent_and_last_good(tmp_path):
    cache = DailyCache(tmp_path)
    today = date(2026, 8, 25)
    old = today - timedelta(days=31)
    recent = today - timedelta(days=3)
    cache.store(old, {"date": old.isoformat()})
    cache.store(recent, {"date": recent.isoformat()})
    cache.prune(keep_days=30, today=today)
    assert cache.load(old) is None
    assert cache.load(recent) is not None
    assert cache.load_last_good() is not None
