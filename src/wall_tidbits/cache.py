import json
import os
import tempfile
from datetime import date
from pathlib import Path

LAST_GOOD_NAME = "last_good.json"


class DailyCache:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.daily_dir = root / "daily"

    def path_for(self, day: date) -> Path:
        return self.daily_dir / f"{day.isoformat()}.json"

    def load(self, day: date) -> dict | None:
        return self._read(self.path_for(day))

    def load_last_good(self) -> dict | None:
        return self._read(self.root / LAST_GOOD_NAME)

    def store(self, day: date, payload: dict) -> None:
        self._write(self.path_for(day), payload)
        self._write(self.root / LAST_GOOD_NAME, payload)

    def prune(self, keep_days: int, today: date) -> None:
        if not self.daily_dir.exists():
            return
        cutoff = today.toordinal() - keep_days
        for path in self.daily_dir.glob("*.json"):
            try:
                day = date.fromisoformat(path.stem)
            except ValueError:
                continue
            if day.toordinal() < cutoff:
                path.unlink(missing_ok=True)

    def _read(self, path: Path) -> dict | None:
        try:
            with open(path) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    def _write(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
