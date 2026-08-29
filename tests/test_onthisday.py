from datetime import date

from wall_tidbits.sources import parse_onthisday

from .conftest import fixture_json

DAY = date(2026, 8, 25)


def test_selects_deterministic_candidate_and_skips_blocked():
    payload = fixture_json("otd_small.json")
    first = parse_onthisday(payload, DAY, family=True)
    again = parse_onthisday(payload, DAY, family=True)
    assert first == again
    assert first is not None
    assert first["text"] != ""
    assert len(first["text"]) <= 230
    assert "killed" not in first["text"].lower()
    assert first["year"] in (2012, 1830)
    assert first["license"].startswith("CC BY-SA")


def test_family_filter_can_be_disabled():
    payload = fixture_json("otd_small.json")
    unfiltered = parse_onthisday(payload, DAY, family=False)
    assert unfiltered is not None


def test_family_filter_does_not_fallback_to_blocked_content():
    payload = {
        "selected": [
            {"text": "A soldier was killed in a skirmish on this day.", "pages": [], "year": 1914},
        ]
    }
    result = parse_onthisday(payload, DAY, family=True)
    assert result is None

    unfiltered = parse_onthisday(payload, DAY, family=False)
    assert unfiltered is not None
    assert "killed" in unfiltered["text"]


def test_returns_none_on_empty_payload():
    assert parse_onthisday({"selected": []}, DAY) is None
    assert parse_onthisday({}, DAY) is None


def test_returns_none_for_malformed_selected_items():
    assert parse_onthisday({"selected": "not-a-list"}, DAY) is None
    assert parse_onthisday({"selected": [None, "not-a-record", 42]}, DAY) is None
