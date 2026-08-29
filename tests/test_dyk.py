from datetime import date

from wall_tidbits.sources import parse_dykwikitext

from .conftest import fixture_json

DAY = date(2026, 8, 25)


def test_parses_real_hooks_deterministically():
    payload = fixture_json("dyk_wikitext.json")
    first = parse_dykwikitext(payload, DAY, family=True)
    again = parse_dykwikitext(payload, DAY, family=True)
    assert first == again
    assert first is not None
    assert first["text"].startswith("That ")
    assert first["text"].endswith("?")
    assert len(first["text"]) <= 200
    assert "pictured" not in first["text"].lower()
    assert "[[" not in first["text"]
    assert first["license"].startswith("CC BY-SA")


def test_skips_pictured_and_unsafe_hooks():
    wikitext = "\n".join(
        [
            "==Hooks==",
            "* ... that '''[[Example Park]]''' ''(pictured)'' is a nice park?",
            "* ... that a governor was executed here in 1600 after a rebellion?",
            "* ... that '''[[Example Bridge]]''' is the longest bridge of its kind in the country?",
        ]
    )
    payload = {"parse": {"wikitext": {"*": wikitext}}}
    result = parse_dykwikitext(payload, DAY, family=True)
    assert result is not None
    assert result["text"] == "That Example Bridge is the longest bridge of its kind in the country?"


def test_returns_none_on_unexpected_payload():
    assert parse_dykwikitext({"error": {}}, DAY) is None
