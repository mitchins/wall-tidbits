from datetime import date
from html import escape

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1404">
<title>Tidbits {date}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ background: #fff; color: #000; }}
  body {{
    font-family: Georgia, "Times New Roman", serif;
    padding: 56px 64px;
    max-width: 1404px;
  }}
  h1 {{
    font-size: 44px;
    font-weight: normal;
    text-align: center;
    letter-spacing: 2px;
    padding-bottom: 10px;
  }}
  .dateline {{
    text-align: center;
    font-size: 26px;
    color: #444;
    border-bottom: 3px solid #000;
    padding-bottom: 24px;
  }}
  section {{ margin-top: 40px; }}
  .label {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 4px;
    text-transform: uppercase;
    border-bottom: 1px solid #999;
    padding-bottom: 6px;
    margin-bottom: 14px;
  }}
  .term {{ font-size: 56px; font-weight: bold; }}
  .pos {{ font-size: 28px; font-style: italic; color: #333; margin-left: 12px; }}
  .body {{ font-size: 34px; line-height: 1.35; }}
  .year {{ font-weight: bold; margin-right: 10px; }}
  .answer {{ font-size: 26px; color: #333; margin-top: 12px; }}
  .answer b {{ font-family: Helvetica, Arial, sans-serif; font-size: 20px; letter-spacing: 3px; }}
  footer {{
    margin-top: 56px;
    border-top: 1px solid #999;
    padding-top: 14px;
    font-family: Helvetica, Arial, sans-serif;
    font-size: 20px;
    color: #555;
    text-align: center;
  }}
  .stale {{ font-size: 22px; color: #555; text-align: center; margin-top: 10px; }}
</style>
</head>
<body>
<h1>TIDBITS</h1>
<div class="dateline">{dateline}{stale_note}</div>

<section>
  <div class="label">Word of the day</div>
  <div><span class="term">{term}</span><span class="pos">{pos}</span></div>
  <div class="body">{definition}</div>
</section>

<section>
  <div class="label">On this day</div>
  <div class="body"><span class="year">{year}</span>{history}</div>
</section>

<section>
  <div class="label">Did you know</div>
  <div class="body">{fact}</div>
</section>

<section>
  <div class="label">Riddle</div>
  <div class="body">{question}</div>
  <div class="answer"><b>ANSWER</b> &nbsp;{answer}</div>
</section>

<footer>{attribution}</footer>
</body>
</html>
"""


def _fmt_date(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%A %d %B %Y")
    except ValueError:
        return iso


def render_display_html(flat: dict) -> str:
    stale = flat.get("stale") or []
    stale_note = ""
    if stale:
        fields = ", ".join(sorted(stale))
        stale_note = f'<div class="stale">(cached: {escape(fields)})</div>'
    return PAGE.format(
        date=escape(flat.get("date", "")),
        dateline=escape(_fmt_date(flat.get("date", ""))),
        stale_note=stale_note,
        term=escape(flat.get("word_term", "") or "\u2014"),
        pos=escape(flat.get("word_part_of_speech", "")),
        definition=escape(flat.get("word_text", "")),
        year=escape(str(flat.get("history_year") or "")),
        history=escape(flat.get("history_text", "")),
        fact=escape(flat.get("fact_text", "") or "\u2014"),
        question=escape(flat.get("riddle_question", "")),
        answer=escape(flat.get("riddle_answer", "")),
        attribution=escape(flat.get("attribution", "")),
    )
