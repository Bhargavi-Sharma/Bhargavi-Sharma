"""Shadbala - six-fold planetary strength (BPHS ch.27), in virupas (60 virupas = 1 rupa).

Approximations are named in APPROXIMATIONS so the report never overstates precision.
"""
from __future__ import annotations

import math

from .constants import (DIG_BALA_HOUSE, GENDER, MEAN_SPEED, NAISARGIKA, OWN_SIGNS, SEVEN, SHADBALA_REQUIRED,
                        SIGN_LORD, SPECIAL_ASPECTS, WEEKDAY_LORD, deg_in_sign, house_from, is_odd)
from .dignity import SAPTAVARGAJA, compound_rel, debil_sign, EXALTATION

APPROXIMATIONS = [
    "Chesta bala for Mars-Saturn uses motion categories from the current speed (vakra, sama, chara...), "
    "not the full cheshta-kendra computation.",
    "Abda (year) and masa (month) lords use 360/30-day counts from the Kali epoch.",
    "Yuddha bala uses the difference of the two planets' other balas.",
    "Dig bala uses the exact ascendant/midheaven degrees (not bhava madhya of a quadrant system).",
]

KALI_EPOCH_JD = 588465.5


def _arc(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def sphuta_drishti(aspecting: str, from_lon: float, to_lon: float) -> float:
    """Graded aspect value in virupas (BPHS ch.26)."""
    d = (to_lon - from_lon) % 360
    if d < 30 or d >= 300:
        v = 0.0
    elif d < 60:
        v = (d - 30) / 2
    elif d < 90:
        v = d - 60 + 15
    elif d < 120:
        v = (120 - d) / 2 + 30
    elif d < 150:
        v = 150 - d
    elif d < 180:
        v = (d - 150) * 2
    else:
        v = (300 - d) / 2
    if aspecting == "Mars" and (90 <= d < 120 or 210 <= d < 240):
        v += 15
    elif aspecting == "Jupiter" and (120 <= d < 150 or 240 <= d < 270):
        v += 30
    elif aspecting == "Saturn" and (60 <= d < 90 or 270 <= d < 300):
        v += 45
    return min(v, 60.0)


def _saptavarga_dignity(p: str, sign: int, deg: float, d1: bool, d1_signs: dict) -> str:
    if d1 and p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        from .constants import MOOLATRIKONA
        s, a, b = MOOLATRIKONA[p]
        if sign == s and a <= deg < b:
            return "Moolatrikona"
    if sign in OWN_SIGNS[p]:
        return "Own"
    return compound_rel(p, SIGN_LORD[sign], d1_signs)


def _benefic(chart, p: str) -> bool:
    if p in ("Jupiter", "Venus"):
        return True
    if p == "Moon":
        return (chart.lon["Moon"] - chart.lon["Sun"]) % 360 <= 180
    if p == "Mercury":
        return not any(q in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") for q in chart.conjunct("Mercury"))
    return False


def compute(chart) -> dict:
    lon = chart.lon
    res = {}
    elong = (lon["Moon"] - lon["Sun"]) % 360
    paksha_arc = elong if elong <= 180 else 360 - elong
    sun = chart.sun
    day_len = sun["sunset"] - sun["sunrise"]
    night_len = sun["next_sunrise"] - sun["sunset"]
    midday = sun["sunrise"] + day_len / 2
    # fraction of the way from local midnight (0) to midday (1)
    dist_from_noon = abs(((chart.jd - midday + 0.5) % 1.0) - 0.5)  # days, 0..0.5
    diurnal = 60 * (1 - dist_from_noon / 0.5)

    if sun["is_day"]:
        third = int((chart.jd - sun["sunrise"]) / (day_len / 3))
        tribhaga_lord = ["Mercury", "Sun", "Saturn"][min(third, 2)]
    else:
        third = int((chart.jd - sun["sunset"]) / (night_len / 3))
        tribhaga_lord = ["Moon", "Venus", "Mars"][min(third, 2)]

    day_num = math.floor(sun["sunrise"] + 0.5 + chart.birth.lon / 360)
    ahargana = day_num - math.floor(KALI_EPOCH_JD + 0.5)
    year_start = day_num - ahargana % 360
    month_start = day_num - ahargana % 30
    abda_lord = WEEKDAY_LORD[(year_start + 1) % 7]
    masa_lord = WEEKDAY_LORD[(month_start + 1) % 7]

    pre = {}
    for p in SEVEN:
        s, deg = chart.sign[p], deg_in_sign(lon[p])
        comp = {}
        # --- Sthana bala
        debil_point = (EXALTATION[p][0] * 30 + EXALTATION[p][1] + 180) % 360
        comp["uchcha"] = _arc(lon[p], debil_point) / 3
        sv = 0.0
        for d in (1, 2, 3, 7, 9, 12, 30):
            vs = chart.vargas[d][p]
            sv += SAPTAVARGAJA[_saptavarga_dignity(p, vs, deg, d == 1, chart.d1_signs)]
        comp["saptavargaja"] = sv
        fem = p in ("Moon", "Venus")
        oj = 0
        for sg in (s, chart.vargas[9][p]):
            oj += 15 if (not is_odd(sg) if fem else is_odd(sg)) else 0
        comp["ojayugma"] = oj
        h = chart.house[p]
        comp["kendradi"] = 60 if h in (1, 4, 7, 10) else 30 if h in (2, 5, 8, 11) else 15
        dk = int(deg // 10)
        comp["drekkana"] = 15 if (GENDER[p] == "M" and dk == 0) or (GENDER[p] == "N" and dk == 1) or \
            (GENDER[p] == "F" and dk == 2) else 0
        sthana = sum(comp.values())
        # --- Dig bala
        strong_point = {1: chart.asc, 4: (chart.snap.mc + 180) % 360, 7: (chart.asc + 180) % 360,
                        10: chart.snap.mc}[DIG_BALA_HOUSE[p]]
        dig = (180 - _arc(lon[p], strong_point)) / 3
        # --- Kala bala
        kala = {}
        kala["nathonnata"] = 60 if p == "Mercury" else diurnal if p in ("Sun", "Jupiter", "Venus") else 60 - diurnal
        ben = _benefic(chart, p)
        pk = paksha_arc / 3 if ben else 60 - paksha_arc / 3
        kala["paksha"] = pk * 2 if p == "Moon" else pk
        kala["tribhaga"] = 60 if p == "Jupiter" or p == tribhaga_lord else 0
        kala["abda"] = 15 if p == abda_lord else 0
        kala["masa"] = 30 if p == masa_lord else 0
        kala["vara"] = 45 if p == sun["vara_lord"] else 0
        kala["hora"] = 60 if p == sun["hora_lord"] else 0
        decl = chart.snap.bodies[p].decl
        if p in ("Moon", "Saturn"):
            ay = (24 - decl) / 48 * 60
        elif p == "Mercury":
            ay = (24 + abs(decl)) / 48 * 60
        else:
            ay = (24 + decl) / 48 * 60
        kala["ayana"] = ay * 2 if p == "Sun" else ay
        # --- Chesta bala
        if p == "Sun":
            chesta = kala["ayana"] / 2
        elif p == "Moon":
            chesta = paksha_arc / 3
        else:
            r = chart.speed(p) / MEAN_SPEED[p]
            chesta = (60 if r < -0.1 else 30 if r < 0 else 15 if r < 0.1 else 15 if r < 0.5 else
                      30 if r < 0.9 else 7.5 if r < 1.1 else 45 if r < 1.5 else 30)
        pre[p] = {"sthana": comp, "sthana_total": sthana, "dig": dig, "kala": kala,
                  "kala_total": sum(kala.values()), "chesta": chesta, "naisargika": NAISARGIKA[p]}

    # --- Drik bala
    for p in SEVEN:
        tot = 0.0
        for q in SEVEN:
            if q == p:
                continue
            v = sphuta_drishti(q, lon[q], lon[p])
            tot += v if _benefic(chart, q) else -v
        pre[p]["drik"] = tot / 4

    # --- Yuddha bala (Mars..Saturn within 1°)
    war = planetary_war(chart)
    for w in war:
        a, b = w["winner"], w["loser"]
        diff = abs((pre[a]["sthana_total"] + pre[a]["dig"] + pre[a]["kala_total"]) -
                   (pre[b]["sthana_total"] + pre[b]["dig"] + pre[b]["kala_total"]))
        pre[a]["kala"]["yuddha"] = diff
        pre[b]["kala"]["yuddha"] = -diff
        for x in (a, b):
            pre[x]["kala_total"] = sum(pre[x]["kala"].values())

    for p in SEVEN:
        r = pre[p]
        total = r["sthana_total"] + r["dig"] + r["kala_total"] + r["chesta"] + r["naisargika"] + r["drik"]
        rupas = total / 60
        uch = r["sthana"]["uchcha"]
        res[p] = {
            "sthana": round(r["sthana_total"], 2), "sthana_parts": {k: round(v, 2) for k, v in r["sthana"].items()},
            "dig": round(r["dig"], 2), "kala": round(r["kala_total"], 2),
            "kala_parts": {k: round(v, 2) for k, v in r["kala"].items()},
            "chesta": round(r["chesta"], 2), "naisargika": r["naisargika"], "drik": round(r["drik"], 2),
            "total_virupas": round(total, 1), "rupas": round(rupas, 2),
            "required_rupas": SHADBALA_REQUIRED[p],
            "ratio": round(rupas / SHADBALA_REQUIRED[p], 2),
            "verdict": "strong" if rupas >= SHADBALA_REQUIRED[p] else "weak",
            "ishta_phala": round(math.sqrt(max(uch, 0) * max(r["chesta"], 0)), 1),
            "kashta_phala": round(math.sqrt(max(60 - uch, 0) * max(60 - r["chesta"], 0)), 1),
        }
    order = sorted(SEVEN, key=lambda p: -res[p]["ratio"])
    return {"planets": res, "rank_by_ratio": order, "approximations": APPROXIMATIONS,
            "abda_lord": abda_lord, "masa_lord": masa_lord, "vara_lord": sun["vara_lord"],
            "hora_lord": sun["hora_lord"]}


WAR_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def planetary_war(chart) -> list[dict]:
    """Graha yuddha: two of Mars..Saturn within 1° of longitude (Surya Siddhanta ch.7)."""
    out = []
    for i, a in enumerate(WAR_PLANETS):
        for b in WAR_PLANETS[i + 1:]:
            if _arc(chart.lon[a], chart.lon[b]) < 1.0:
                la, lb = chart.snap.bodies[a].lat, chart.snap.bodies[b].lat
                winner, loser = (a, b) if la >= lb else (b, a)
                alt = "Venus" if "Venus" in (a, b) else winner
                out.append({"planets": [a, b], "separation": round(_arc(chart.lon[a], chart.lon[b]), 3),
                            "winner": winner, "loser": loser,
                            "variant_winner_by_brightness": alt,
                            "variants_agree": alt == winner,
                            "source": "Surya Siddhanta 7 (northern planet wins); brightness rule as variant"})
    return out
