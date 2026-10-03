"""Jaimini elements: chara karakas, arudha padas, upapada, karakamsha, longevity by three pairs."""
from __future__ import annotations

from . import ephemeris as eph
from .constants import MODALITY, PLANETS, SEVEN, SIGN_LORD, SIGNS, house_from, sign_of

KARAKA7 = ["Atmakaraka (self/soul)", "Amatyakaraka (career/advisor)", "Bhratrikaraka (siblings/guru)",
           "Matrikaraka (mother)", "Putrakaraka (children)", "Gnatikaraka (rivals/disease)",
           "Darakaraka (spouse)"]
KARAKA8 = KARAKA7[:4] + ["Pitrikaraka (father)"] + KARAKA7[4:]


def chara_karakas(chart, count: int) -> list[dict]:
    degs = {p: chart.lon[p] % 30 for p in SEVEN}
    if count == 8:
        degs["Rahu"] = 30 - (chart.lon["Rahu"] % 30)  # Rahu counted backwards (BPHS ch.32)
    order = sorted(degs, key=lambda p: -degs[p])
    names = KARAKA8 if count == 8 else KARAKA7
    return [{"karaka": names[i], "planet": p, "degree_used": round(degs[p], 3)} for i, p in enumerate(order)]


def _lord(chart, sign: int) -> str:
    """Dual lordship of Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu): stronger = more conjunct planets,
    then higher degree (Jaimini Sutras 1.2; one of several rules - see notes)."""
    if sign == 7:
        pair = ("Mars", "Ketu")
    elif sign == 10:
        pair = ("Saturn", "Rahu")
    else:
        return SIGN_LORD[sign]
    a, b = pair
    ca, cb = len(chart.conjunct(a)), len(chart.conjunct(b))
    if ca != cb:
        return a if ca > cb else b
    return a if chart.lon[a] % 30 >= chart.lon[b] % 30 else b


def arudha(chart, house: int) -> int:
    hs = (chart.lagna + house - 1) % 12
    lord = _lord(chart, hs)
    n = house_from(hs, chart.sign[lord])
    pada = (chart.sign[lord] + n - 1) % 12
    if pada == hs or pada == (hs + 6) % 12:  # exception: same or 7th -> take 10th from there
        pada = (pada + 9) % 12
    return pada


def padas(chart) -> dict:
    out = {}
    for h in range(1, 13):
        s = arudha(chart, h)
        label = {1: "Arudha Lagna (AL - image/status)", 12: "Upapada (UL - marriage)"}.get(h, f"A{h}")
        out[label] = {"sign": SIGNS[s], "house_from_lagna": house_from(chart.lagna, s),
                      "occupants": [p for p in PLANETS if chart.sign[p] == s]}
    return out


def hora_lagna(chart) -> float:
    snap = eph.snapshot(chart.sun["sunrise"], chart.settings)
    hours = (chart.jd - chart.sun["sunrise"]) * 24
    return (snap.bodies["Sun"].lon + hours * 30) % 360


def _span(a: int, b: int) -> str:
    m = {MODALITY[a], MODALITY[b]}
    if m == {"Movable"} or m == {"Fixed", "Dual"}:
        return "Long (Purna)"
    if m == {"Movable", "Fixed"} or m == {"Dual"}:
        return "Medium (Madhya)"
    return "Short (Alpa)"


def longevity(chart) -> dict:
    """Jaimini Sutras 2.1: three pairs of signs give the longevity compartment."""
    l1, l8 = chart.lord_of_house(1), chart.lord_of_house(8)
    hl = sign_of(hora_lagna(chart))
    pairs = [
        {"pair": f"Lagna lord {l1} & 8th lord {l8}", "span": _span(chart.sign[l1], chart.sign[l8])},
        {"pair": "Lagna & Moon sign", "span": _span(chart.lagna, chart.moon_sign)},
        {"pair": f"Lagna & Hora Lagna ({SIGNS[hl]})", "span": _span(chart.lagna, hl)},
    ]
    spans = [p["span"] for p in pairs]
    best = max(set(spans), key=spans.count)
    if spans.count(best) == 1:
        best = pairs[2]["span"]
        rule = "all three differ: Lagna-Hora Lagna pair decides (Jaimini 2.1 commentary)"
    else:
        rule = "majority of the three pairs"
    order = ["Short (Alpa)", "Medium (Madhya)", "Long (Purna)"]
    modifiers = []
    jh = chart.house["Jupiter"]
    if jh in (1, 7) and chart.dig["Jupiter"] != "Debilitated":
        modifiers.append("Jupiter in lagna/7th unafflicted: longevity raised one compartment (kakshya vriddhi)")
        best = order[min(order.index(best) + 1, 2)]
    if "Saturn" in (l1, l8) and chart.dig["Saturn"] not in ("Exalted", "Own", "Moolatrikona"):
        modifiers.append("Saturn is one of the deciding lords: commentators reduce within the compartment "
                         "(kakshya hrasa) - applied as a caution only")
    return {"pairs": pairs, "category": best, "rule_used": rule, "modifiers": modifiers,
            "ranges_years": {"Short (Alpa)": "up to ~32-36", "Medium (Madhya)": "~32/36 to ~64/72",
                             "Long (Purna)": "~64/72 to ~96-108"},
            "caution": "Classical texts (BPHS ch.44) themselves warn that longevity is the hardest judgement; "
                       "this compartment is one indicator among several and is never converted into a date."}


def karakamsha(chart, karakas: list[dict]) -> dict:
    ak = karakas[0]["planet"]
    ks = chart.vargas[9][ak]
    return {"atmakaraka": ak, "karakamsha_sign": SIGNS[ks],
            "planets_in_karakamsha_in_d9": [p for p in PLANETS if chart.vargas[9][p] == ks],
            "12th_from_karakamsha_d9": [p for p in PLANETS if chart.vargas[9][p] == (ks + 11) % 12]}


def report(chart) -> dict:
    n = chart.settings["chara_karaka_count"]
    k7 = chara_karakas(chart, 7)
    k8 = chara_karakas(chart, 8)
    active = k8 if n == 8 else k7
    differ = [a["karaka"] for a, b in zip(k7, k8) if a["planet"] != b["planet"]]
    return {"chara_karakas": active, "scheme": f"{n}-karaka (default {n})",
            "other_scheme_differs": bool(differ), "other_scheme": k8 if n == 7 else k7,
            "arudha_padas": padas(chart), "karakamsha": karakamsha(chart, active),
            "longevity": longevity(chart)}
