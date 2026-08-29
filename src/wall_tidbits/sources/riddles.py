import json
from datetime import date
from pathlib import Path

from wall_tidbits.normalize import budget, stable_index

QUESTION_BUDGET = 180
ANSWER_BUDGET = 80


def load_riddles(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return [r for r in data if r.get("question") and r.get("answer")]


def pick_riddle(riddles: list[dict], day: date, seed: str) -> dict | None:
    if not riddles:
        return None
    chosen = riddles[stable_index(f"{seed}:{day.isoformat()}", len(riddles))]
    return {
        "question": budget(str(chosen["question"]), QUESTION_BUDGET),
        "answer": budget(str(chosen["answer"]), ANSWER_BUDGET),
        "source": str(chosen.get("source") or "local"),
        "license": str(chosen.get("license") or "original"),
    }
