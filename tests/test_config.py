from wall_tidbits.config import load_settings


def test_build_on_start_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("BUILD_ON_START", "yes")
    assert load_settings().build_on_start is True

    monkeypatch.setenv("BUILD_ON_START", "0")
    assert load_settings().build_on_start is False
