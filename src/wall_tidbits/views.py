ATTRIBUTION = "Wiktionary \u00b7 Wikipedia \u00b7 CC BY-SA"


def flat_view(payload: dict) -> dict:
    word = payload.get("word") or {}
    history = payload.get("history") or {}
    riddle = payload.get("riddle") or {}
    fact = payload.get("fact") or {}
    return {
        "date": payload.get("date", ""),
        "timezone": payload.get("timezone", ""),
        "word_term": word.get("term", ""),
        "word_part_of_speech": word.get("part_of_speech", ""),
        "word_text": word.get("text", ""),
        "history_year": history.get("year"),
        "history_text": history.get("text", ""),
        "riddle_question": riddle.get("question", ""),
        "riddle_answer": riddle.get("answer", ""),
        "fact_text": fact.get("text", ""),
        "stale": payload.get("stale") or [],
        "attribution": ATTRIBUTION,
    }


def credits_view(payload: dict) -> dict:
    sources = []
    for field in ("word", "history", "fact", "riddle"):
        item = payload.get(field)
        if not item:
            continue
        sources.append(
            {
                "field": field,
                "source": item.get("source", ""),
                "source_url": item.get("source_url", ""),
                "license": item.get("license", ""),
            }
        )
    return {"date": payload.get("date", ""), "sources": sources}
