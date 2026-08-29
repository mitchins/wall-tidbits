import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEZONE = "Australia/Sydney"
DEFAULT_USER_AGENT = "wall-tidbits-gateway/0.1"


@dataclass(frozen=True)
class Settings:
    timezone: str = DEFAULT_TIMEZONE
    contact_email: str = ""
    cache_dir: Path = Path("data/cache")
    riddles_path: Path | None = None
    public_token: str = ""
    retention_days: int = 30
    riddle_seed: str = "wall-tidbits"
    fetch_timeout: float = 20.0
    content_filter: str = "family"
    user_agent: str = DEFAULT_USER_AGENT
    build_on_start: bool = True

    def effective_user_agent(self) -> str:
        if self.contact_email:
            return f"{self.user_agent} (contact: {self.contact_email})"
        return self.user_agent

    def family_filter_enabled(self) -> bool:
        return self.content_filter.strip().lower() == "family"


def load_settings() -> Settings:
    return Settings(
        timezone=os.environ.get("TIMEZONE", DEFAULT_TIMEZONE),
        contact_email=os.environ.get("CONTACT_EMAIL", ""),
        cache_dir=Path(os.environ.get("CACHE_DIR", "data/cache")),
        riddles_path=(
            Path(value) if (value := os.environ.get("RIDDLES_PATH")) else None
        ),
        public_token=os.environ.get("PUBLIC_TOKEN", ""),
        retention_days=int(os.environ.get("RETENTION_DAYS", "30")),
        riddle_seed=os.environ.get("RIDDLE_SEED", "wall-tidbits"),
        fetch_timeout=float(os.environ.get("FETCH_TIMEOUT", "20")),
        content_filter=os.environ.get("CONTENT_FILTER", "family"),
        build_on_start=os.environ.get("BUILD_ON_START", "true").strip().lower()
        in ("true", "1", "yes"),
    )
