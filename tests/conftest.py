from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wall_tidbits.app import create_app
from wall_tidbits.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"
DATA = Path(__file__).parent.parent / "data"
DAY = "2026-08-25"

WOTD_URL = "https://en.wiktionary.org/w/api.php"
OTD_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/08/25"
DYK_PARAMS = {"action": "parse", "page": "Template:Did_you_know"}


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text()


def fixture_json(name: str):
    import json

    return json.loads(fixture_text(name))


@pytest.fixture
def settings(tmp_path):
    return Settings(
        timezone="Australia/Sydney",
        cache_dir=tmp_path / "cache",
        riddles_path=DATA / "riddles.json",
        public_token="t0ken123",
        riddle_seed="test-seed",
        build_on_start=False,
    )


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c
