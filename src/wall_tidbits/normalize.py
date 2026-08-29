import hashlib
import html
import re

STYLE_RE = re.compile(r"<style.*?</style>", re.S)
SCRIPT_RE = re.compile(r"<script.*?</script>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
WIKILINK_RE = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")

FAMILY_BLOCKLIST = (
    "kill",
    "massacre",
    "murder",
    "execut",
    "genocide",
    "war crime",
    "torture",
    "assassinat",
    "bomb",
    "shoot",
    "behead",
    "suicide",
    "rape",
)


def strip_html(raw: str) -> str:
    text = STYLE_RE.sub(" ", raw)
    text = SCRIPT_RE.sub(" ", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    return tidy_ws(text)


def tidy_ws(text: str) -> str:
    return WS_RE.sub(" ", text).strip()


def tidy_parens(text: str) -> str:
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\(\s*\)", "", text)
    return tidy_ws(text)


def clean_wikitext_line(line: str) -> str:
    text = WIKILINK_RE.sub(r"\1", line)
    text = text.replace("'''", "").replace("''", "")
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return tidy_ws(html.unescape(text))


def budget(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for sep in (". ", "? ", "! ", "; "):
        idx = cut.rfind(sep)
        if idx > 40:
            return cut[: idx + 1].strip()
    idx = cut.rfind(" ")
    trimmed = cut[:idx].rstrip(" ,;:-") if idx > 0 else cut
    return trimmed + "\u2026"


def stable_index(seed: str, modulo: int) -> int:
    digest = hashlib.sha256(seed.encode()).digest()
    return int.from_bytes(digest[:8], "big") % max(modulo, 1)


def family_safe(text: str) -> bool:
    low = text.lower()
    return not any(word in low for word in FAMILY_BLOCKLIST)
