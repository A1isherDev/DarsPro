"""DarsPro — tarif cheklovlari (CLAUDE.md "Tariflar va cheklovlar" jadvali).

None = cheksiz.
"""
from .models import Plan

# Oylik o'yin yaratish limiti (ContentItem, source=teacher)
MONTHLY_CREATE_LIMIT = {
    Plan.FREE: 0,
    Plan.START: 15,
    Plan.PRO: None,
    Plan.MAX: None,
}

# Sinf (live) rejimida maksimal o'quvchi soni
MAX_PLAYERS = {
    Plan.FREE: 10,
    Plan.START: 30,
    Plan.PRO: 100,
    Plan.MAX: 500,
}


def monthly_create_limit(plan):
    return MONTHLY_CREATE_LIMIT.get(plan, 0)


def max_players(plan):
    return MAX_PLAYERS.get(plan, 10)
