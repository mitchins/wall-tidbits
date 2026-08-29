from datetime import date

from wall_tidbits.sources import load_riddles, pick_riddle

from .conftest import DATA

DAY = date(2026, 8, 25)


def test_loads_bundled_corpus():
    riddles = load_riddles(DATA / "riddles.json")
    assert len(riddles) >= 20
    assert all(r["question"] and r["answer"] for r in riddles)


def test_pick_is_deterministic_per_day_and_seed():
    riddles = load_riddles(DATA / "riddles.json")
    first = pick_riddle(riddles, DAY, "seed-a")
    again = pick_riddle(riddles, DAY, "seed-a")
    other_seed = pick_riddle(riddles, DAY, "seed-b")
    assert first == again
    assert first is not None
    assert first["question"]
    assert first["answer"]
    assert other_seed is not None


def test_pick_respects_budgets():
    riddles = [
        {
            "question": "What? " + "word " * 60,
            "answer": "Answer. " + "word " * 40,
        }
    ]
    picked = pick_riddle(riddles, DAY, "seed")
    assert len(picked["question"]) <= 180
    assert len(picked["answer"]) <= 80


def test_pick_returns_none_when_empty():
    assert pick_riddle([], DAY, "seed") is None
