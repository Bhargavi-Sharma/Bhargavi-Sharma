"""Functional nature of planets for a lagna (BPHS ch.34), plus planet states:
combustion, retrogression, gandanta, and a per-planet condition summary."""
from __future__ import annotations

from .constants import (MODALITY, NAK_SPAN, NATURAL_BENEFICS, PLANETS, SEVEN, SIGN_LORD, SIGNS,
                        deg_in_sign)
from .dignity import DIGNITY_SCORE

NB = ["Jupiter", "Venus", "Mercury", "Moon"]


def functional_nature(chart) -> dict:
    out = {}
    for p in SEVEN:
        owned = chart.houses_owned(p)
        notes, score = [], 0
        is_lagna_lord = 1 in owned
        kendras = [h for h in owned if h in (4, 7, 10)]
        trines = [h for h in owned if h in (5, 9)]
        yogakaraka = bool(kendras and trines)
        for h in owned:
            if h in (1, 5, 9):
                score += 3
            elif h in (4, 7, 10):
                if p in NB:
                    score -= 1
                    notes.append(f"kendradhipati dosha: natural benefic owning house {h}")
            elif h in (3, 6, 11):
                score -= 2
            elif h == 8:
                if p in ("Sun", "Moon"):
                    notes.append("8th lordship blemish does not apply to Sun/Moon (BPHS 34)")
                elif not is_lagna_lord:
                    score -= 2
        if 2 in owned or 7 in owned:
            notes.append("maraka (lord of 2nd/7th) - can bring health crises or endings in its periods")
        if is_lagna_lord:
            verdict = "Benefic (lagna lord - always auspicious)"
        elif yogakaraka:
            verdict = "Yogakaraka (owns kendra + trikona - best benefic)"
        elif score > 0:
            verdict = "Benefic"
        elif score < 0:
            verdict = "Malefic"
        else:
            verdict = "Neutral (gives results by association/placement)"
        out[p] = {"owns": owned, "verdict": verdict, "score": score, "notes": notes}
    for node in ("Rahu", "Ketu"):
        disp = SIGN_LORD[chart.sign[node]]
        out[node] = {"owns": [], "verdict": f"Acts like its dispositor {disp} and conjunct planets",
                     "dispositor": disp, "dispositor_verdict": out[disp]["verdict"], "score": out[disp]["score"],
                     "notes": ["Nodes give the results of the sign lord and of planets they join (BPHS 34/47)"]}
    mod = MODALITY[chart.lagna]
    badhaka_house = {"Movable": 11, "Fixed": 9, "Dual": 7}[mod]
    return {"planets": out, "badhaka_house": badhaka_house, "badhaka_lord": chart.lord_of_house(badhaka_house),
            "maraka_lords": sorted({chart.lord_of_house(2), chart.lord_of_house(7)}),
            "yogakarakas": [p for p, v in out.items() if v["verdict"].startswith("Yogakaraka")]}


def combustion(chart) -> dict:
    orbs = chart.settings["combustion_orbs"]
    out = {}
    for p in ("Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        d = abs((chart.lon[p] - chart.lon["Sun"] + 180) % 360 - 180)
        key = f"{p}_retro" if chart.retro(p) and f"{p}_retro" in orbs else p
        orb = orbs[key]
        if d <= orb:
            out[p] = {"distance_from_sun": round(d, 2), "orb": orb, "combust": True,
                      "deep": d <= orb / 2,
                      "note": ("Mercury is combust in most charts; many authors treat its combustion as mild"
                               if p == "Mercury" else "")}
    return out


def gandanta(chart) -> list[dict]:
    """Junction of water and fire signs: last 3°20' of Cancer/Scorpio/Pisces, first 3°20' of Leo/Sagittarius/Aries."""
    span = NAK_SPAN / 4
    items = [("Lagna", chart.asc)] + [(p, chart.lon[p]) for p in PLANETS]
    out = []
    for name, lon in items:
        s, d = int(lon // 30), deg_in_sign(lon)
        if (s in (3, 7, 11) and d >= 30 - span) or (s in (4, 8, 0) and d <= span):
            out.append({"point": name, "sign": SIGNS[s], "degree": round(d, 2),
                        "note": "Gandanta: a knot between water and fire signs - weakness/turbulence for its significations"})
    return out


def planet_condition(chart, comb: dict, war: list, shad: dict, func: dict) -> dict:
    """A transparent, additive summary of every factor that strengthens or weakens each planet."""
    out = {}
    lost_war = {w["loser"] for w in war}
    for p in PLANETS:
        plus, minus = [], []
        dig = chart.dig[p]
        sc = DIGNITY_SCORE.get(dig, 0)
        (plus if sc > 0 else minus if sc < 0 else plus).append(f"dignity: {dig}")
        if chart.vargas[9][p] == chart.sign[p]:
            plus.append("vargottama (same sign in D1 and D9)")
        from .dignity import dignity
        nd = dignity(p, chart.vargas[9][p], 0, chart.d1_signs, use_mt=False)
        if nd in ("Exalted", "Own"):
            plus.append(f"navamsa dignity: {nd}")
        elif nd == "Debilitated":
            minus.append("debilitated in navamsa")
        h = chart.house[p]
        if h in (1, 4, 7, 10):
            plus.append(f"in kendra (house {h})")
        if h in (5, 9):
            plus.append(f"in trikona (house {h})")
        if h in (6, 8, 12):
            minus.append(f"in dusthana (house {h})")
        if p in comb:
            minus.append(f"combust ({comb[p]['distance_from_sun']}° from Sun)")
        if p in lost_war:
            minus.append("defeated in planetary war")
        if p in SEVEN:
            if chart.retro(p) and p not in ("Sun", "Moon"):
                plus.append("retrograde: full chesta bala (BPHS); results often delayed or repeated")
            r = shad["planets"][p]["ratio"]
            (plus if r >= 1 else minus).append(f"shadbala {shad['planets'][p]['rupas']} rupas ({r}x required)")
        av = chart.planet_row(p)["baladi_avastha"]
        if av.startswith(("Mrita", "Vriddha")):
            minus.append(f"baladi avastha {av}")
        elif av.startswith("Yuva"):
            plus.append(f"baladi avastha {av}")
        ben = [q for q in chart.planet_aspected_by(p) if q in NATURAL_BENEFICS]
        mal = [q for q in chart.planet_aspected_by(p) if q not in NATURAL_BENEFICS]
        if ben:
            plus.append(f"aspected by benefics {ben}")
        if mal:
            minus.append(f"aspected by malefics {mal}")
        conj_mal = [q for q in chart.conjunct(p) if q in ("Saturn", "Mars", "Rahu", "Ketu")]
        if conj_mal:
            minus.append(f"conjunct malefics {conj_mal}")
        out[p] = {"strengths": plus, "weaknesses": minus, "net": len(plus) - len(minus),
                  "functional": func["planets"][p]["verdict"]}
    return out
