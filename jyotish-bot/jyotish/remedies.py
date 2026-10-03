"""Remedies (upay): gemstones with their exceptions, mantra/daan, and Lal Kitab structure.

Gem rules here are the common Parashari-practice rules (functional nature decides, condition
decides how much). The classical texts themselves say little about gems; this is stated in the output.
"""
from __future__ import annotations

from .constants import NATURAL_FRIENDS, PLANETS, SEVEN
from .dignity import baladi_avastha

GEMS = {
    "Sun": {"gem": "Ruby (Manik)", "upratna": "Red garnet / red spinel", "finger": "ring", "metal": "gold or copper",
            "day": "Sunday morning (Sun hora)", "weight": "3-5 carat", "alt_finger": None},
    "Moon": {"gem": "Pearl (Moti)", "upratna": "Moonstone", "finger": "little", "metal": "silver",
             "day": "Monday evening / Shukla paksha", "weight": "5-7 carat", "alt_finger": "ring"},
    "Mars": {"gem": "Red Coral (Moonga)", "upratna": "Carnelian", "finger": "ring", "metal": "gold or copper",
             "day": "Tuesday morning", "weight": "6-9 carat", "alt_finger": None},
    "Mercury": {"gem": "Emerald (Panna)", "upratna": "Peridot / green tourmaline", "finger": "little",
                "metal": "gold or bronze", "day": "Wednesday morning", "weight": "3-6 carat", "alt_finger": None},
    "Jupiter": {"gem": "Yellow Sapphire (Pukhraj)", "upratna": "Citrine / yellow topaz", "finger": "index",
                "metal": "gold", "day": "Thursday morning", "weight": "3-5 carat", "alt_finger": None},
    "Venus": {"gem": "Diamond (Heera)", "upratna": "White sapphire / zircon / opal", "finger": "middle",
              "metal": "silver or platinum", "day": "Friday morning", "weight": "0.5-1 carat (white sapphire 3-5)",
              "alt_finger": "ring (many practitioners) - finger rule differs by tradition"},
    "Saturn": {"gem": "Blue Sapphire (Neelam)", "upratna": "Amethyst / iolite", "finger": "middle",
               "metal": "silver, panchdhatu or iron", "day": "Saturday evening", "weight": "3-5 carat",
               "alt_finger": None},
    "Rahu": {"gem": "Hessonite (Gomed)", "upratna": "Orange zircon", "finger": "middle",
             "metal": "silver or panchdhatu", "day": "Saturday evening", "weight": "5-8 carat", "alt_finger": None},
    "Ketu": {"gem": "Cat's Eye (Lehsunia)", "upratna": "Tiger's eye", "finger": "little",
             "metal": "silver", "day": "Tuesday or Thursday", "weight": "3-5 carat",
             "alt_finger": "ring (some traditions)"},
}

MANTRA = {
    "Sun": ("ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", 7000, "Aditya Hridayam; offer water at sunrise",
            "wheat, jaggery, copper, red cloth - Sunday"),
    "Moon": ("ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः", 11000, "Shiva worship; serve mother",
             "rice, milk, silver, white cloth - Monday"),
    "Mars": ("ॐ क्रां क्रीं क्रौं सः भौमाय नमः", 10000, "Hanuman Chalisa; Kartikeya",
             "masoor dal, jaggery, red cloth - Tuesday"),
    "Mercury": ("ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", 9000, "Vishnu Sahasranama",
                "green moong, green cloth, feed cows green fodder - Wednesday"),
    "Jupiter": ("ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", 19000, "respect teachers/elders; Vishnu",
                "chana dal, turmeric, yellow cloth, books - Thursday"),
    "Venus": ("ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", 16000, "Lakshmi/Durga worship",
              "rice, ghee, curd, white cloth, perfume - Friday"),
    "Saturn": ("ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", 23000, "Shani stotra; Hanuman; serve workers",
               "black sesame, mustard oil, iron, black cloth - Saturday"),
    "Rahu": ("ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः", 18000, "Durga Saptashati",
             "urad, blanket, coconut - Saturday"),
    "Ketu": ("ॐ स्रां स्रीं स्रौं सः केतवे नमः", 17000, "Ganesha worship",
             "multi-coloured blanket, sesame, feed dogs - Tuesday/Saturday"),
}


def _enemies(p: str) -> set[str]:
    if p in NATURAL_FRIENDS:
        e = set(NATURAL_FRIENDS[p]["enemies"])
    else:
        e = {"Sun", "Moon"}
    if p in ("Sun", "Moon"):
        e |= {"Rahu", "Ketu"}
    return e


def gem_advice(chart, func: dict, cond: dict, shad: dict, comb: dict) -> dict:
    recs = []
    for p in PLANETS:
        f = func["planets"][p]
        verdict = f["verdict"]
        owned = f["owns"]
        reasons, cautions = [], []
        deg = chart.lon[p] % 30
        av = baladi_avastha(chart.sign[p], deg)
        if p in ("Rahu", "Ketu"):
            status = "avoid unless specifically indicated"
            if chart.house[p] in (3, 6, 10, 11):
                status = "conditional (trial first)"
                reasons.append(f"{p} in upachaya house {chart.house[p]} gives good results")
            cautions.append("node gems act fast and unpredictably - 3-day trial (keep under pillow) is customary")
        elif verdict.startswith(("Benefic", "Yogakaraka")):
            weak = []
            if shad["planets"][p]["ratio"] < 1:
                weak.append(f"shadbala {shad['planets'][p]['ratio']}x of required")
            if chart.dig[p] in ("Debilitated", "Enemy", "Great Enemy"):
                weak.append(f"dignity {chart.dig[p]}")
            if p in comb:
                weak.append("combust")
            if av.startswith(("Mrita", "Bala", "Vriddha")):
                weak.append(f"degree state {av}")
            if weak:
                status = "recommended (functional benefic that is weak)"
                reasons += [f"{verdict}; owns houses {owned}"] + weak
            else:
                status = "optional (functional benefic already strong)"
                reasons.append(f"{verdict}; already strong - gem adds little")
            if chart.house[p] in (6, 8, 12):
                cautions.append(f"placed in dusthana {chart.house[p]} - a gem also amplifies that house's troubles; "
                                "many practitioners prefer mantra/daan here")
            if chart.dig[p] == "Debilitated":
                cautions.append("debilitated: traditions differ on gems for debilitated planets "
                                "(check the Neecha Bhanga result)")
            if 2 in owned or 7 in owned:
                cautions.append("also a maraka (2nd/7th lord) - watch health during its periods")
        elif verdict.startswith("Malefic"):
            status = "avoid"
            reasons.append(f"functional malefic for this lagna (owns {owned}) - strengthening it strengthens problems")
        else:
            status = "neutral - only if strongly indicated by a specific problem"
            reasons.append(f"{verdict}; owns {owned}")
        if 0 <= deg < 1 or deg > 29:
            cautions.append("planet at a sign junction (rashi sandhi) - results erratic, gem effect uncertain")
        recs.append({"planet": p, "status": status, **GEMS[p], "reasons": reasons, "cautions": cautions})

    wearable = [r for r in recs if r["status"].startswith(("recommended", "optional"))]
    conflicts = []
    for i, a in enumerate(wearable):
        for b in wearable[i + 1:]:
            if b["planet"] in _enemies(a["planet"]) or a["planet"] in _enemies(b["planet"]):
                conflicts.append(f"{a['gem']} ({a['planet']}) and {b['gem']} ({b['planet']}) are natural enemies - "
                                 "do not wear together; choose the one for the more important house/dasha")
            elif a["finger"] == b["finger"]:
                conflicts.append(f"{a['gem']} and {b['gem']} share the {a['finger']} finger - wear on separate hands "
                                 "or pick one")
    return {"recommendations": recs, "conflicts": conflicts,
            "general_rules": [
                "Gems strengthen a planet, they do not make a malefic good. Lagna lord, 5th and 9th lords and a "
                "yogakaraka are the usual candidates; lords of 3, 6, 8, 11 are avoided unless they also own a trikona.",
                "The gem of the running mahadasha/antardasha lord is considered only if that lord is a functional benefic.",
                "Natural gems of good clarity; weight scales with body weight in most traditions.",
                "Wear on the working hand on the planet's day/hora after energising with its mantra (108 times).",
                "The classical texts (BPHS etc.) prescribe mantra, daan and worship; gem therapy is from later "
                "Ratna-shastra and modern practice.",
            ]}


def mantra_daan(chart, func: dict, cond: dict) -> list[dict]:
    out = []
    for p in PLANETS:
        weak = cond[p]["net"] < 0
        mal = func["planets"][p]["verdict"].startswith("Malefic") or p in ("Rahu", "Ketu")
        if weak or mal:
            m, n, deity, daan = MANTRA[p]
            out.append({"planet": p, "why": ("weak" if weak else "") + (" & " if weak and mal else "") +
                        ("functional malefic / node" if mal else ""),
                        "beej_mantra": m, "japa_count": n, "worship": deity, "daan": daan})
    return out


# ----------------------------------------------------------------- Lal Kitab
LK_PAKKA_GHAR = {"Sun": [1], "Moon": [4], "Mars": [3, 8], "Mercury": [7], "Jupiter": [2, 5, 9, 12],
                 "Venus": [7], "Saturn": [8, 10], "Rahu": [12], "Ketu": [6]}
LK_EXALT = {"Sun": [1], "Moon": [2], "Mars": [10], "Mercury": [6], "Jupiter": [4], "Venus": [12],
            "Saturn": [7], "Rahu": [3, 6], "Ketu": [9, 12]}
LK_DEBIL = {"Sun": [7], "Moon": [8], "Mars": [4], "Mercury": [12], "Jupiter": [10], "Venus": [6],
            "Saturn": [1], "Rahu": [8, 9], "Ketu": [3, 6]}
LK_ASPECT = {1: [7], 2: [6], 3: [9, 11], 4: [10], 5: [9], 6: [12], 8: [2]}
LK_GENERAL = {
    "Sun": "offer water to the rising Sun; flow a copper coin in running water; avoid taking things for free",
    "Moon": "serve mother and take her blessings; keep silver; keep a vessel of water/milk by the bed at night "
            "and pour it on a tree in the morning",
    "Mars": "distribute sweets; keep a red handkerchief; respect brothers; feed sweet roti to animals",
    "Mercury": "feed green fodder to cows; respect sisters/daughters/aunts; avoid green clothing if Mercury is bad",
    "Jupiter": "apply saffron/turmeric tilak; serve elders and teachers; water a peepal tree",
    "Venus": "respect spouse; donate curd/ghee/camphor; feed cows",
    "Saturn": "feed crows; offer mustard oil; avoid alcohol and meat; serve labourers; keep honesty in dealings",
    "Rahu": "flow coal or barley in running water; keep a solid silver ball; avoid blue clothes and liquor",
    "Ketu": "feed dogs; donate a black-white blanket; respect sons/nephews; wear gold in the ear (traditional)",
}
LK_RIN = [
    ("Pitru Rin (ancestral debt)", lambda h: [p for p in ("Venus", "Mercury", "Rahu") if h[p] in (2, 5, 9, 12)],
     "collect money from every family member and donate together on one day"),
    ("Matri Rin (mother's debt)", lambda h: ["Ketu"] if h["Ketu"] == 4 else [],
     "collect silver from family members and flow it in running water"),
    ("Stri Rin (debt to women)", lambda h: [p for p in ("Sun", "Rahu", "Ketu") if h[p] in (2, 7)],
     "feed 100 cows on one day with family contribution"),
    ("Sambandhi Rin (relatives)", lambda h: [p for p in ("Mercury", "Ketu") if h[p] in (1, 8)],
     "help a relative's family at a ceremony with joint contribution"),
    ("Behen/Beti Rin (sister/daughter)", lambda h: ["Moon"] if h["Moon"] in (3, 6) else [],
     "distribute yellow cowries/sweets to girls with family contribution"),
    ("Nirdayi Rin (cruelty)", lambda h: [p for p in ("Sun", "Moon", "Mars") if h[p] in (10, 11)],
     "feed 100 labourers in one day with family contribution"),
    ("Ajanma Rin (unborn)", lambda h: [p for p in ("Sun", "Venus", "Mars") if h[p] == 12],
     "collect coconuts from family members and flow in water"),
]


def lal_kitab(chart) -> dict:
    h = chart.house
    rows = []
    for p in PLANETS:
        state = ("exalted (LK)" if h[p] in LK_EXALT[p] else "debilitated (LK)" if h[p] in LK_DEBIL[p] else
                 "in pakka ghar" if h[p] in LK_PAKKA_GHAR[p] else "ordinary")
        sleeping = None
        if h[p] in LK_ASPECT:
            sleeping = not any(chart.occupants(x) for x in LK_ASPECT[h[p]])
        rows.append({"planet": p, "lk_house": h[p], "state": state, "pakka_ghar": LK_PAKKA_GHAR[p],
                     "soya_sleeping": sleeping, "general_remedy": LK_GENERAL[p]})
    rins = []
    for name, f, rem in LK_RIN:
        who = f(h)
        if who:
            rins.append({"rin": name, "caused_by": who, "remedy": rem})
    sleeping_houses = [x for x in range(1, 13) if not chart.occupants(x) and not chart.aspected_by(x)]
    return {"planets": rows, "rin": rins, "sleeping_houses": sleeping_houses,
            "notes": ["Lal Kitab (1939-1952 editions, Pt. Roop Chand Joshi) uses houses only - signs are ignored "
                      "and house 1 is always treated as Aries.",
                      "Lal Kitab rules often contradict Parashari rules; when they do, the report shows both and "
                      "does not merge them.",
                      "Do one remedy at a time for 40-43 days; avoid remedies of a planet that is exalted in LK."]}
