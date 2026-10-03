"""Planetary relationships and dignity (BPHS ch.3)."""
from .constants import (EXALTATION, MOOLATRIKONA, NATURAL_FRIENDS, OWN_SIGNS, SIGN_LORD,
                        house_from, is_odd)

# Node tables follow the default in variants.py (Taurus/Scorpio). Treated as tentative.
NODE_EXALT = {"Rahu": 1, "Ketu": 7}
NODE_DEBIL = {"Rahu": 7, "Ketu": 1}
NODE_OWN = {"Rahu": [10], "Ketu": [7]}
NODE_FRIENDS = {"Rahu": ["Venus", "Saturn", "Mercury"], "Ketu": ["Mars", "Venus", "Saturn"]}
NODE_ENEMIES = {"Rahu": ["Sun", "Moon", "Mars"], "Ketu": ["Sun", "Moon"]}


def natural_rel(p: str, q: str) -> str:
    if p in NODE_FRIENDS:
        return "F" if q in NODE_FRIENDS[p] else "E" if q in NODE_ENEMIES[p] else "N"
    if q in ("Rahu", "Ketu"):
        return "N"
    t = NATURAL_FRIENDS[p]
    return "F" if q in t["friends"] else "E" if q in t["enemies"] else "N"


def temporal_rel(sign_p: int, sign_q: int) -> str:
    """Tatkalika: planets in 2,3,4,10,11,12 from each other are temporary friends (BPHS 3.55)."""
    return "F" if house_from(sign_p, sign_q) in (2, 3, 4, 10, 11, 12) else "E"


_COMPOUND = {("F", "F"): "Great Friend", ("F", "E"): "Neutral", ("N", "F"): "Friend",
             ("N", "E"): "Enemy", ("E", "F"): "Neutral", ("E", "E"): "Great Enemy"}


def compound_rel(p: str, q: str, d1_signs: dict[str, int]) -> str:
    if p == q:
        return "Self"
    return _COMPOUND[(natural_rel(p, q), temporal_rel(d1_signs[p], d1_signs[q]))]


def exalt_sign(p: str) -> int:
    return NODE_EXALT[p] if p in NODE_EXALT else EXALTATION[p][0]


def debil_sign(p: str) -> int:
    return NODE_DEBIL[p] if p in NODE_DEBIL else (EXALTATION[p][0] + 6) % 12


def dignity(p: str, sign: int, deg: float, d1_signs: dict[str, int], use_mt: bool = True) -> str:
    """Dignity label for planet p placed in `sign` at `deg` (deg used only for D1 moolatrikona)."""
    if sign == exalt_sign(p):
        # Moon/Mercury: exaltation sign also holds moolatrikona/own degrees
        if use_mt and p in MOOLATRIKONA and MOOLATRIKONA[p][0] == sign:
            mt = MOOLATRIKONA[p]
            if p == "Mercury" and deg >= mt[1]:
                return "Moolatrikona" if deg < mt[2] else "Own"
            if p == "Moon" and deg >= mt[1]:
                return "Moolatrikona"
        return "Exalted"
    if sign == debil_sign(p):
        return "Debilitated"
    if use_mt and p in MOOLATRIKONA:
        s, a, b = MOOLATRIKONA[p]
        if sign == s and a <= deg < b:
            return "Moolatrikona"
    own = NODE_OWN.get(p) or OWN_SIGNS.get(p, [])
    if sign in own:
        return "Own"
    return compound_rel(p, SIGN_LORD[sign], d1_signs)


DIGNITY_SCORE = {"Exalted": 5, "Moolatrikona": 4, "Own": 3.5, "Great Friend": 3, "Friend": 2,
                 "Neutral": 1, "Enemy": -1, "Great Enemy": -2, "Debilitated": -4, "Self": 3.5}

# Saptavargaja bala virupas (BPHS ch.27)
SAPTAVARGAJA = {"Moolatrikona": 45, "Own": 30, "Great Friend": 22.5, "Friend": 15, "Neutral": 7.5,
                "Enemy": 3.75, "Great Enemy": 1.875, "Exalted": 30, "Debilitated": 1.875}


def baladi_avastha(sign: int, deg: float) -> str:
    """Age state by degree (BPHS ch.45). Odd signs: infant->dead; even signs reversed."""
    names = ["Bala (infant, 25% results)", "Kumara (youth, 50%)", "Yuva (adult, 100%)",
             "Vriddha (old, ~10%)", "Mrita (dead, ~0%)"]
    i = min(int(deg // 6), 4)
    return names[i] if is_odd(sign) else names[4 - i]


def jagradadi_avastha(dig: str) -> str:
    """Awake/dreaming/sleeping (BPHS ch.45)."""
    if dig in ("Exalted", "Own", "Moolatrikona"):
        return "Jagrat (awake - full results)"
    if dig in ("Great Friend", "Friend", "Neutral"):
        return "Swapna (dreaming - medium results)"
    return "Sushupti (sleeping - weak results)"
