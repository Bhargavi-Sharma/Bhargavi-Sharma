"""Doshas with their cancellation rules. Each is labelled with how classical it is."""
from __future__ import annotations

from .constants import GANDMOOL, PLANETS, SEVEN, SIGNS, house_from
from .chart import nakshatra_of

KAAL_SARP_NAMES = {1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal", 5: "Padma", 6: "Mahapadma",
                   7: "Takshak", 8: "Karkotak", 9: "Shankhachood", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag"}


def _d(name, present, details, cancellations, classical, effect, severity=None):
    if not present:
        status = "absent"
    elif cancellations:
        status = "present but cancelled/reduced"
    else:
        status = "present"
    return {"name": name, "present": present, "status": status, "details": details,
            "cancellations": cancellations, "classical_status": classical, "effect": effect,
            "severity": severity}


def mangal_dosha(chart) -> dict:
    mh = (1, 2, 4, 7, 8, 12)
    refs = {"Lagna": chart.lagna, "Moon": chart.moon_sign, "Venus": chart.sign["Venus"]}
    hits = {k: house_from(v, chart.sign["Mars"]) for k, v in refs.items()
            if house_from(v, chart.sign["Mars"]) in mh}
    canc = []
    ms = chart.sign["Mars"]
    if ms in (0, 7):
        canc.append("Mars in own sign (Aries/Scorpio)")
    if ms == 9:
        canc.append("Mars exalted (Capricorn)")
    if "Jupiter" in chart.conjunct("Mars") or "Jupiter" in chart.planet_aspected_by("Mars"):
        canc.append("Jupiter conjoins/aspects Mars")
    if "Moon" in chart.conjunct("Mars"):
        canc.append("Mars with Moon (Chandra-Mangala)")
    h = chart.house["Mars"]
    popular = {2: (2, 5), 12: (1, 6), 4: (0, 7), 7: (3, 9), 8: (8, 11), 1: (4, 10)}
    if h in popular and ms in popular[h]:
        canc.append(f"Mars in house {h} in {SIGNS[ms]} (popular regional exception list)")
    if chart.house["Jupiter"] == 1 or chart.house["Venus"] == 1:
        canc.append("Jupiter or Venus in lagna")
    severity = None
    if hits:
        severity = "high" if len(hits) == 3 else "medium" if len(hits) == 2 else "low"
    return _d("Mangal (Kuja) Dosha", bool(hits),
              {"from": hits, "mars_house_from_lagna": h,
               "note": "Matching practice: dosha is neutralised if the partner has a comparable dosha."},
              canc if hits else [],
              "Not in BPHS as a named dosha; comes from muhurta/marriage-matching literature and regional practice",
              "friction, delay or strain in marriage; Mars energy needs a channel", severity)


def kaal_sarp(chart) -> dict:
    r = chart.lon["Rahu"]
    span = lambda x: (x - r) % 360  # 0..180 is the Rahu->Ketu half
    sides = [span(chart.lon[p]) < 180 for p in SEVEN]
    full = all(sides) or not any(sides)
    outside = [p for p, s in zip(SEVEN, sides) if s != (sum(sides) >= 4)]
    partial = len(outside) == 1
    present = full or partial
    kind = KAAL_SARP_NAMES[chart.house["Rahu"]]
    canc = []
    if partial:
        canc.append(f"partial: {outside[0]} is outside the Rahu-Ketu axis")
    if present and any(chart.lon[p] % 30 == chart.lon["Rahu"] % 30 for p in SEVEN):
        pass
    if present:
        conj = [p for p in SEVEN if p in chart.conjunct("Rahu") or p in chart.conjunct("Ketu")]
        if conj:
            canc.append(f"{conj} conjunct a node - many practitioners consider the yoga broken by a planet on the axis")
    return _d(f"Kaal Sarp ({kind})" if present else "Kaal Sarp", present,
              {"rahu_house": chart.house["Rahu"], "direction": "Rahu->Ketu" if sum(sides) >= 4 else "Ketu->Rahu"},
              canc, "NOT in BPHS, Brihat Jataka, Saravali or Phaladeepika - a later/popular combination",
              "phases of obstruction followed by sudden rise; never used alone to predict events")


def pairs(chart) -> list[dict]:
    out = []
    specs = [
        ("Grahan Dosha (Sun)", "Sun", ("Rahu", "Ketu"), "eclipse of Sun: father, ego, authority, health",
         "Popular; BPHS ch.83 mentions Sun-node afflictions among causes of curses (shapa)"),
        ("Grahan Dosha (Moon)", "Moon", ("Rahu", "Ketu"), "eclipse of Moon: anxiety, mother, emotional instability",
         "Popular; Moon-node results in Saravali/BPHS"),
        ("Guru Chandal", "Jupiter", ("Rahu", "Ketu"), "ethics/guru/children issues, unorthodox beliefs",
         "Popular name; Jupiter-Rahu conjunction results are classical"),
        ("Shrapit", "Saturn", ("Rahu",), "delays, karmic burdens", "Modern/popular combination, not classical"),
        ("Angarak", "Mars", ("Rahu", "Ketu"), "anger, accidents, impulsive acts", "Popular"),
        ("Vish Yoga", "Moon", ("Saturn",), "depressive tendencies, emotional heaviness, delays",
         "Popular; Moon-Saturn conjunction results described in Saravali"),
    ]
    for name, a, bs, eff, cls in specs:
        hit = [b for b in bs if b in chart.conjunct(a)]
        canc = []
        if hit and "Jupiter" in chart.planet_aspected_by(a) and a != "Jupiter":
            canc.append("Jupiter aspects the afflicted planet")
        if hit and chart.dig[a] in ("Exalted", "Own", "Moolatrikona"):
            canc.append(f"{a} strong by sign ({chart.dig[a]})")
        out.append(_d(name, bool(hit), {"with": hit, "house": chart.house[a] if hit else None}, canc, cls, eff))
    return out


def pitru_dosha(chart) -> dict:
    reasons = []
    l9 = chart.lord_of_house(9)
    for x in ("Rahu", "Ketu", "Saturn"):
        if x in chart.conjunct("Sun"):
            reasons.append(f"Sun with {x}")
        if chart.house[x] == 9:
            reasons.append(f"{x} in 9th house")
        if x in chart.conjunct(l9) and l9 != x:
            reasons.append(f"9th lord {l9} with {x}")
    canc = []
    if reasons and ("Jupiter" in chart.aspected_by(9) or chart.house["Jupiter"] == 9):
        canc.append("Jupiter aspects/occupies the 9th house")
    return _d("Pitru Dosha", bool(reasons), {"reasons": reasons}, canc,
              "Based on BPHS ch.83-84 (curses from past life: pitri shapa) as summarised by later authors",
              "obstacles linked to father/ancestors, progeny delays, fortune blocked until remedies")


def gandmool(chart) -> dict:
    n = nakshatra_of(chart.lon["Moon"])
    present = n["name"] in GANDMOOL
    sev = None
    if present:
        idx = GANDMOOL.index(n["name"])
        junction_pada = 4 if n["name"] in ("Ashlesha", "Jyeshtha", "Revati") else 1
        sev = "high (junction pada)" if n["pada"] == junction_pada else "mild"
    return _d("Gandmool", present, {"moon_nakshatra": n["name"], "pada": n["pada"]}, [],
              "Muhurta tradition (e.g. Muhurta Chintamani); Shanti traditionally done on the 27th day",
              "early-life health/family disturbances per pada; mostly a birth-time ritual concern", sev)


def detect(chart) -> list[dict]:
    return [mangal_dosha(chart), kaal_sarp(chart), pitru_dosha(chart), gandmool(chart)] + pairs(chart)
