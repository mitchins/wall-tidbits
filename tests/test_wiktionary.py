from datetime import date

from wall_tidbits.sources import parse_wotd

from .conftest import fixture_text


def test_parses_real_entry_for_exact_date():
    result = parse_wotd(fixture_text("wotd.atom"), date(2026, 8, 25))
    assert result is not None
    assert result["term"] == "demake"
    assert result["part_of_speech"] == "noun"
    assert result["text"].startswith("(video games) A remake")
    assert result["text"].endswith("older platform.")
    assert " ." not in result["text"] and "( " not in result["text"]
    assert len(result["text"]) <= 170
    assert "August_25" in result["source_url"]
    assert result["license"].startswith("CC BY-SA")


def test_falls_back_to_nearest_earlier_entry():
    result = parse_wotd(fixture_text("wotd.atom"), date(2026, 8, 26))
    assert result is not None
    assert result["term"] == "demake"


def test_returns_none_when_no_earlier_entry():
    assert parse_wotd(fixture_text("wotd.atom"), date(2026, 8, 1)) is None


def test_returns_none_on_invalid_xml():
    assert parse_wotd("<not-atom>", date(2026, 8, 25)) is None
