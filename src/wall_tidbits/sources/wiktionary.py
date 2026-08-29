import re
import xml.etree.ElementTree as ET
from datetime import date

from wall_tidbits.normalize import budget, strip_html, tidy_parens

ATOM_NS = "http://www.w3.org/2005/Atom"

FEED_URL = "https://en.wiktionary.org/w/api.php?action=featuredfeed&feed=wotd&feedformat=atom"

POS_MAP = {
    "n": "noun",
    "v": "verb",
    "adj": "adjective",
    "adv": "adverb",
    "pron": "pronoun",
    "prep": "preposition",
    "conj": "conjunction",
    "interj": "interjection",
    "num": "numeral",
}

TITLE_RE = re.compile(r'id="WOTD-rss-title"\s*>([^<]+)<')
POS_RE = re.compile(r'WOTD-rss-title">.*?</a></b>\s*<i>([^<]{1,16})</i>', re.S)


def wotd_archive_url(day: date) -> str:
    month = day.strftime("%B")
    return f"https://en.wiktionary.org/wiki/Wiktionary:Word_of_the_day/{day.year}/{month}_{day.day}"


async def fetch_word_of_the_day(client, day: date) -> dict | None:
    resp = await client.get(FEED_URL)
    resp.raise_for_status()
    return parse_wotd(resp.text, day)


def parse_wotd(xml_text: str, day: date) -> dict | None:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    exact = None
    nearest = None
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        updated = (entry.findtext(f"{{{ATOM_NS}}}updated") or "")[:10]
        summary = entry.findtext(f"{{{ATOM_NS}}}summary") or ""
        if not updated or not summary:
            continue
        if updated == day.isoformat():
            exact = summary
        elif updated < day.isoformat() and (nearest is None or updated > nearest[0]):
            nearest = (updated, summary)
    summary = exact or (nearest[1] if nearest else None)
    if not summary:
        return None
    return extract_wotd(summary, day)


def extract_wotd(summary_html: str, day: date) -> dict | None:
    title_match = TITLE_RE.search(summary_html)
    if not title_match:
        return None
    term = strip_html(title_match.group(1))
    if not term:
        return None
    pos_match = POS_RE.search(summary_html)
    pos_raw = strip_html(pos_match.group(1)) if pos_match else ""
    part_of_speech = POS_MAP.get(pos_raw, pos_raw)
    definition = ""
    desc_start = summary_html.find('id="WOTD-rss-description"')
    if desc_start != -1:
        li_match = re.search(r"<li>(.*?)</li>", summary_html[desc_start:], re.S)
        if li_match:
            definition = tidy_parens(strip_html(li_match.group(1)))
    if not definition:
        return None
    return {
        "term": term,
        "part_of_speech": part_of_speech,
        "text": budget(definition, 170),
        "source": "Wiktionary",
        "source_url": wotd_archive_url(day),
        "license": "CC BY-SA 4.0",
    }
