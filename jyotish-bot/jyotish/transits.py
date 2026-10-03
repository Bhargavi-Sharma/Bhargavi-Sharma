"""Gochar (transits) from the Moon with vedha (Phaladeepika ch.26), ashtakavarga support,
Sade Sati / Dhaiya, and double transit of Jupiter + Saturn (K.N. Rao's timing technique)."""
from __future__ import annotations

from datetime import datetime, timezone

from . import ephemeris as eph
from .constants import PLANETS, SIGNS, SIGN_LORD, SPECIAL_ASPECTS, house_from, sign_of

# favourable houses from natal Moon -> vedha (obstruction) house
GOCHAR = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn": {3: 12, 6: 9, 11: 5},
    "Rahu": {3: 12, 6: 9, 11: 5},
    "Ketu": {3: 12, 6: 9, 11: 5},
}
NO_VEDHA_PAIRS = [{"Sun", "Saturn"}, {"Moon", "Mercury"}]  # father-son pairs do not obstruct each other


def transit_report(chart, when: datetime, av: dict) -> dict:
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    snap = eph.snapshot(eph.julday(when.astimezone(timezone.utc)), chart.settings)
    M = chart.moon_sign
    tsign = {p: sign_of(snap.bodies[p].lon) for p in PLANETS}
    rows = []
    for p in PLANETS:
        s = tsign[p]
        hm = house_from(M, s)
        good = hm in GOCHAR[p]
        vedha_by = []
        if good:
            vh = GOCHAR[p][hm]
            vedha_by = [q for q in PLANETS if q != p and house_from(M, tsign[q]) == vh
                        and {p, q} not in NO_VEDHA_PAIRS]
        bindus = av["bav"][p][s] if p in av["bav"] else None
        verdict = ("favourable" if good and not vedha_by else "favourable but obstructed (vedha)" if good
                   else "unfavourable")
        if bindus is not None:
            verdict += f"; {bindus} bindus in own BAV ({'supports' if bindus >= 4 else 'weakens'})"
        rows.append({"planet": p, "sign": SIGNS[s], "degree": round(snap.bodies[p].lon % 30, 2),
                     "retrograde": snap.bodies[p].speed < 0, "house_from_lagna": house_from(chart.lagna, s),
                     "house_from_moon": hm, "sav_bindus_of_sign": av["sav"][s], "verdict": verdict,
                     "vedha_by": vedha_by, "over_natal": [q for q in PLANETS if chart.sign[q] == s]})
    sat = house_from(M, tsign["Saturn"])
    sade = None
    if sat in (12, 1, 2):
        sade = {12: "Sade Sati phase 1 (rising) - expenses, restlessness",
                1: "Sade Sati phase 2 (peak) - pressure on mind/body, hard lessons",
                2: "Sade Sati phase 3 (setting) - finances/family strain easing"}[sat]
    elif sat == 4:
        sade = "Kantaka/Ardhashtama Shani (4th from Moon) - home/peace disturbed"
    elif sat == 8:
        sade = "Ashtama Shani (8th from Moon) - obstacles, health, sudden setbacks"
    return {"date": when.strftime("%Y-%m-%d"), "planets": rows, "saturn_from_moon": sat,
            "sade_sati_or_dhaiya": sade,
            "double_transit_houses_from_lagna": double_transit_houses(chart.lagna, tsign)}


def _influenced_houses(base: int, sign: int, planet: str) -> set[int]:
    h = house_from(base, sign)
    asp = SPECIAL_ASPECTS.get(planet, [7])
    return {h} | {(h + n - 2) % 12 + 1 for n in asp}


def double_transit_houses(lagna: int, tsign: dict) -> list[int]:
    """Houses (from lagna) that both Jupiter and Saturn occupy or aspect by transit."""
    j = _influenced_houses(lagna, tsign["Jupiter"], "Jupiter")
    s = _influenced_houses(lagna, tsign["Saturn"], "Saturn")
    return sorted(j & s)


def slow_positions(jd: float, settings: dict) -> dict:
    snap = eph.snapshot(jd, settings)
    return {p: sign_of(snap.bodies[p].lon) for p in ("Jupiter", "Saturn", "Rahu", "Ketu", "Mars", "Sun")}


def sade_sati_periods(chart, start: datetime, years: int = 60) -> list[dict]:
    """Saturn's passage through 12th, 1st, 2nd from Moon (and 4th/8th dhaiya), scanned every 5 days."""
    jd0 = eph.julday(start.astimezone(timezone.utc))
    M = chart.moon_sign
    spans, cur, cur_start = [], None, None
    step = 5.0
    n = int(years * 365.25 / step)
    for i in range(n + 1):
        jd = jd0 + i * step
        s = sign_of(eph.snapshot(jd, chart.settings).bodies["Saturn"].lon)
        h = house_from(M, s)
        tag = ("Sade Sati" if h in (12, 1, 2) else "Ashtama Shani" if h == 8 else
               "Kantaka Shani" if h == 4 else None)
        if tag != cur or i == n:
            if cur:
                spans.append([cur, cur_start, jd])
            cur, cur_start = tag, jd
    merged = []  # join fragments split by a retrograde dip back into the previous sign
    for sp in spans:
        if merged and merged[-1][0] == sp[0] and sp[1] - merged[-1][2] < 400:
            merged[-1][2] = sp[2]
        else:
            merged.append(sp)
    fmt = lambda jd: eph.jd_to_utc(jd).strftime("%Y-%m")
    return [{"type": t, "start": fmt(a), "end": fmt(b)} for t, a, b in merged]
