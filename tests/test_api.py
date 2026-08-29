import dataclasses
from datetime import date

import httpx
import respx

from .conftest import DAY, DYK_PARAMS, OTD_URL, WOTD_URL, fixture_json, fixture_text

DYK_URL = "https://en.wikipedia.org/w/api.php"
HTML_CONTENT_TYPE = "text/html"


def mock_upstream():
    respx.get(WOTD_URL).respond(200, text=fixture_text("wotd.atom"))
    respx.get(OTD_URL).respond(200, json=fixture_json("otd_small.json"))
    respx.get(DYK_URL, params=DYK_PARAMS).respond(200, json=fixture_json("dyk_wikitext.json"))


@respx.mock
def test_daily_endpoint_builds_and_caches(client):
    mock_upstream()
    first = client.get("/v1/daily", params={"date": DAY})
    assert first.status_code == 200
    body = first.json()
    assert body["date"] == DAY
    assert body["timezone"] == "Australia/Sydney"
    assert body["word"]["term"] == "demake"
    assert body["history"]["text"]
    assert body["fact"]["text"].endswith("?")
    assert body["riddle"]["question"]
    assert body["stale"] == []

    second = client.get("/v1/daily", params={"date": DAY})
    assert second.json() == body
    assert respx.get(WOTD_URL).call_count == 1


@respx.mock
def test_display_json_flat_shape(client):
    mock_upstream()
    resp = client.get("/v1/display.json", params={"date": DAY})
    assert resp.status_code == 200
    assert set(resp.json()) == {
        "date",
        "timezone",
        "word_term",
        "word_part_of_speech",
        "word_text",
        "history_year",
        "history_text",
        "riddle_question",
        "riddle_answer",
        "fact_text",
        "stale",
        "attribution",
    }
    assert resp.json()["word_term"] == "demake"


@respx.mock
def test_display_html_renders_escaped_content(client):
    mock_upstream()
    resp = client.get("/v1/display.html", params={"date": DAY})
    assert resp.status_code == 200
    assert HTML_CONTENT_TYPE in resp.headers["content-type"]
    assert "demake" in resp.text
    assert "Wiktionary" in resp.text


@respx.mock
def test_credits_lists_all_sources(client):
    mock_upstream()
    resp = client.get("/v1/credits", params={"date": DAY})
    assert resp.status_code == 200
    sources = resp.json()["sources"]
    assert {s["field"] for s in sources} == {"word", "history", "fact", "riddle"}
    assert all(s["license"] for s in sources)
    assert all(s["source_url"] or s["source"] == "local" for s in sources)


@respx.mock
def test_token_routes_serve_and_reject(client):
    mock_upstream()
    ok = client.get("/e/t0ken123/daily.json", params={"date": DAY})
    assert ok.status_code == 200
    assert ok.json()["word"]["term"] == "demake"

    html_resp = client.get("/e/t0ken123/display.html", params={"date": DAY})
    assert html_resp.status_code == 200

    assert client.get("/e/wrongtoken/daily.json", params={"date": DAY}).status_code == 404
    assert client.get("/e/t0ken123/bogus.json", params={"date": DAY}).status_code == 404


def test_token_routes_disabled_without_token(settings):
    from fastapi.testclient import TestClient

    from wall_tidbits.app import create_app

    app = create_app(dataclasses.replace(settings, public_token=""))
    with TestClient(app) as c:
        assert c.get("/e/t0ken123/daily.json", params={"date": DAY}).status_code == 404


def test_rejects_bad_and_future_dates(client):
    assert client.get("/v1/daily", params={"date": "not-a-date"}).status_code == 400
    assert client.get("/v1/daily", params={"date": "2099-01-01"}).status_code == 400


@respx.mock
def test_upstream_outage_falls_back_to_last_good(client):
    respx.get(WOTD_URL).mock(side_effect=httpx.ConnectError("down"))
    respx.get(OTD_URL).mock(side_effect=httpx.ConnectError("down"))
    respx.get(DYK_URL, params=DYK_PARAMS).mock(side_effect=httpx.ConnectError("down"))

    last_good = {
        "date": "2026-08-24",
        "timezone": "Australia/Sydney",
        "generated_at": "2026-08-24T00:05:00+00:00",
        "word": {"term": "old-word", "text": "old definition"},
        "history": {"year": 1900, "text": "old history"},
        "fact": {"text": "Old fact?"},
        "riddle": {"question": "Old?", "answer": "Yes."},
        "stale": [],
    }
    client.app.state.cache.store(date(2026, 8, 24), last_good)

    resp = client.get("/v1/daily", params={"date": DAY})
    assert resp.status_code == 200
    body = resp.json()
    assert body["word"]["term"] == "old-word"
    assert body["history"]["text"] == "old history"
    assert body["fact"]["text"] == "Old fact?"
    assert sorted(body["stale"]) == ["fact", "history", "word"]
    assert body["riddle"]["question"]
