from .dyk import fetch_fact_of_the_day, parse_dykwikitext
from .onthisday import fetch_on_this_day, parse_onthisday
from .riddles import load_riddles, pick_riddle
from .wiktionary import fetch_word_of_the_day, parse_wotd

__all__ = [
    "fetch_fact_of_the_day",
    "fetch_on_this_day",
    "fetch_word_of_the_day",
    "load_riddles",
    "parse_dykwikitext",
    "parse_onthisday",
    "parse_wotd",
    "pick_riddle",
]
