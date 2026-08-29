import re
from datetime import date

from wall_tidbits.normalize import budget, clean_wikitext_line, family_safe, stable_index

API_URL = (
    "https://en.wikipedia.org/w/api.php?action=parse"
    "&page=Template:Did_you_know&prop=wikitext&format=json"
)

MAX_LEN = 200

PICTURED_RE = re.compile(r"\(pictured\)", re.IGNORECASE)


async def fetch_fact_of_the_day(client, day: date, family: bool = True) -> dict | None:
    resp = await client.get(API_URL)
    resp.raise_for_status()
    return parse_dykwikitext(resp.json(), day, family)


def parse_dykwikitext(payload: dict, day: date, family: bool = True) -> dict | None:
    try:
        wikitext = payload["parse"]["wikitext"]["*"]
    except (KeyError, TypeError):
        return None
    hooks = []
    for line in wikitext.splitlines():
        stripped = line.strip()
        if not stripped.startswith("*") or "that" not in stripped[:30]:
            continue
        if PICTURED_RE.search(stripped):
            continue
        hook = clean_wikitext_line(stripped.lstrip("* "))
        if hook.startswith("..."):
            hook = hook[3:].strip()
        if not hook.startswith("That") and not hook.startswith("that"):
            continue
        hook = hook[0].upper() + hook[1:]
        if len(hook) > MAX_LEN or not hook.endswith("?"):
            continue
        if "{{" in hook or "[[" in hook:
            continue
        if family and not family_safe(hook):
            continue
        hooks.append(hook)
    if not hooks:
        return None
    chosen = hooks[stable_index(day.isoformat(), len(hooks))]
    return {
        "text": budget(chosen, MAX_LEN),
        "source": "Wikipedia Did You Know",
        "source_url": "https://en.wikipedia.org/wiki/Template:Did_you_know",
        "license": "CC BY-SA 4.0",
    }
