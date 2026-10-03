"""Yogas with their formation conditions AND their cancellation / weakening conditions.

Each yoga is reported with: present, planets, conditions met, cancellations found, the net
verdict ("active", "weakened", "cancelled"), its source and its classical result.
"""
from __future__ import annotations

from .constants import (EXALTATION, OWN_SIGNS, PLANETS, SEVEN, SIGN_LORD, SIGNS, house_from)
from .dignity import debil_sign, exalt_sign

BENEFICS = ["Jupiter", "Venus", "Mercury"]
MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]


def _y(name, category, planets, conditions, cancellations, source, result, weakenings=None):
    weakenings = weakenings or []
    verdict = "cancelled" if cancellations else "weakened" if weakenings else "active"
    return {"name": name, "category": category, "planets": planets, "conditions": conditions,
            "cancellations": cancellations, "weakenings": weakenings, "verdict": verdict,
            "source": source, "result": result}


def _afflictions(chart, p, comb, war_losers) -> list[str]:
    w = []
    if p in comb:
        w.append(f"{p} combust")
    if p in war_losers:
        w.append(f"{p} lost planetary war")
    if chart.dig.get(p) == "Debilitated":
        w.append(f"{p} debilitated")
    if chart.house[p] in (6, 8, 12):
        w.append(f"{p} in dusthana {chart.house[p]}")
    nodes = [q for q in chart.conjunct(p) if q in ("Rahu", "Ketu")]
    if nodes and p not in ("Rahu", "Ketu"):
        w.append(f"{p} conjunct {nodes[0]} (eclipsed/obsessive quality)")
    return w


def _kendra_from(chart, p, ref_sign) -> bool:
    return house_from(ref_sign, chart.sign[p]) in (1, 4, 7, 10)


def detect(chart, comb: dict, war: list, shad: dict) -> list[dict]:
    Y = []
    losers = {w["loser"] for w in war}
    L, M = chart.lagna, chart.moon_sign

    # ---- Pancha Mahapurusha (BPHS ch.75, Phaladeepika ch.6)
    names = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavya", "Saturn": "Shasha"}
    results = {"Ruchaka": "courage, command, land, martial success", "Bhadra": "intellect, eloquence, business skill",
               "Hamsa": "wisdom, righteousness, respect", "Malavya": "luxury, beauty, spouse, vehicles, arts",
               "Shasha": "authority over many, organisational power, wealth via labour/masses"}
    for p, n in names.items():
        strong_sign = chart.sign[p] in OWN_SIGNS[p] or chart.sign[p] == EXALTATION[p][0]
        if strong_sign and chart.house[p] in (1, 4, 7, 10):
            weak = _afflictions(chart, p, comb, losers)
            if any(q in ("Sun", "Moon") for q in chart.conjunct(p)):
                weak.append(f"{p} conjunct Sun/Moon - some commentators on Phaladeepika say results come only in its own dasha")
            if shad["planets"][p]["ratio"] < 1:
                weak.append(f"{p} shadbala below required ({shad['planets'][p]['ratio']}x)")
            Y.append(_y(f"{n} (Pancha Mahapurusha)", "Mahapurusha", [p],
                        [f"{p} in {SIGNS[chart.sign[p]]} ({chart.dig[p]}) in kendra {chart.house[p]} from lagna"],
                        [], "BPHS ch.75; Phaladeepika ch.6", results[n], weak))
        elif strong_sign and _kendra_from(chart, p, M):
            Y.append(_y(f"{n} from Moon (secondary)", "Mahapurusha", [p],
                        [f"{p} own/exalted in kendra from Moon (not from lagna)"], [],
                        "Some authors count from Moon too; BPHS counts from lagna", results[n],
                        ["formed from Moon only - weaker than from lagna"]))

    # ---- Gajakesari (BPHS ch.36; Phaladeepika ch.6)
    if house_from(M, chart.sign["Jupiter"]) in (1, 4, 7, 10):
        weak = _afflictions(chart, "Jupiter", comb, losers)
        if chart.dig["Moon"] == "Debilitated":
            weak.append("Moon debilitated")
        if (chart.lon["Moon"] - chart.lon["Sun"]) % 360 < 72 or (chart.lon["Moon"] - chart.lon["Sun"]) % 360 > 288:
            weak.append("Moon dark (near new moon) - weak Moon")
        Y.append(_y("Gajakesari", "Lunar", ["Jupiter", "Moon"],
                    [f"Jupiter in house {house_from(M, chart.sign['Jupiter'])} from Moon"], [],
                    "BPHS ch.36; Phaladeepika ch.6; Jataka Parijata", "fame, intelligence, lasting reputation, "
                    "victory over rivals", weak))

    # ---- Lunar yogas: Sunapha, Anapha, Durudhara, Kemadruma (Brihat Jataka 13; BPHS 37)
    excl = ("Sun", "Rahu", "Ketu", "Moon")
    second = [p for p in PLANETS if p not in excl and house_from(M, chart.sign[p]) == 2]
    twelfth = [p for p in PLANETS if p not in excl and house_from(M, chart.sign[p]) == 12]
    if second and twelfth:
        Y.append(_y("Durudhara", "Lunar", second + twelfth, [f"{second} in 2nd and {twelfth} in 12th from Moon"],
                    [], "Brihat Jataka ch.13; BPHS ch.37", "wealth, vehicles, generosity, comforts"))
    elif second:
        Y.append(_y("Sunapha", "Lunar", second, [f"{second} in 2nd from Moon"], [], "Brihat Jataka ch.13; BPHS ch.37",
                    "self-earned wealth, good intellect and reputation"))
    elif twelfth:
        Y.append(_y("Anapha", "Lunar", twelfth, [f"{twelfth} in 12th from Moon"], [], "Brihat Jataka ch.13; BPHS ch.37",
                    "good health, pleasing personality, renunciation late in life"))
    else:
        canc = []
        kendra_l = [p for p in SEVEN if p != "Moon" and chart.house[p] in (1, 4, 7, 10)]
        kendra_m = [p for p in SEVEN if p != "Moon" and house_from(M, chart.sign[p]) in (4, 7, 10)]
        if kendra_l:
            canc.append(f"planets in kendra from lagna: {kendra_l} (BPHS ch.37; Phaladeepika ch.6)")
        if kendra_m:
            canc.append(f"planets in kendra from Moon: {kendra_m} (Phaladeepika ch.6)")
        if "Jupiter" in chart.planet_aspected_by("Moon"):
            canc.append("Jupiter aspects the Moon")
        if chart.conjunct("Moon"):
            canc.append(f"Moon conjunct {chart.conjunct('Moon')} (Saravali)")
        Y.append(_y("Kemadruma", "Lunar (dosha)", ["Moon"], ["no planet (except Sun/nodes) in 2nd or 12th from Moon"],
                    canc, "Brihat Jataka ch.13; BPHS ch.37; Phaladeepika ch.6 (cancellations)",
                    "poverty, sorrow, dependence, mental unrest - if not cancelled"))

    # ---- Solar yogas: Vesi, Vasi, Ubhayachari (BPHS ch.38)
    S = chart.sign["Sun"]
    ex = ("Moon", "Rahu", "Ketu", "Sun")
    v2 = [p for p in PLANETS if p not in ex and house_from(S, chart.sign[p]) == 2]
    v12 = [p for p in PLANETS if p not in ex and house_from(S, chart.sign[p]) == 12]
    if v2 and v12:
        Y.append(_y("Ubhayachari", "Solar", v2 + v12, [f"{v2} 2nd and {v12} 12th from Sun"], [], "BPHS ch.38",
                    "king-like, eloquent, balanced, prosperous"))
    elif v2:
        Y.append(_y("Vesi", "Solar", v2, [f"{v2} in 2nd from Sun"], [], "BPHS ch.38",
                    "truthful, balanced; results follow the nature of the planet (benefic good, malefic mixed)"))
    elif v12:
        Y.append(_y("Vasi", "Solar", v12, [f"{v12} in 12th from Sun"], [], "BPHS ch.38",
                    "skilful, charitable, happy; results follow the planet's nature"))

    # ---- Budhaditya
    if chart.sign["Mercury"] == chart.sign["Sun"]:
        canc = []
        if "Mercury" in comb and comb["Mercury"]["deep"]:
            canc.append(f"Mercury deeply combust ({comb['Mercury']['distance_from_sun']}°)")
        Y.append(_y("Budhaditya", "Combination", ["Sun", "Mercury"], ["Sun and Mercury in the same sign"], [],
                    "Popular (derived from BPHS/Saravali Sun-Mercury conjunction results)",
                    "intelligence, skill, good reputation", canc))

    # ---- Chandra-Mangala (BPHS / Phaladeepika 6)
    if chart.sign["Moon"] == chart.sign["Mars"] or (house_from(chart.sign["Moon"], chart.sign["Mars"]) == 7):
        Y.append(_y("Chandra-Mangala", "Combination", ["Moon", "Mars"], ["Moon and Mars conjunct or opposite"], [],
                    "Phaladeepika ch.6", "earning through trade/enterprise; can indicate harshness to mother"))

    # ---- Adhi yoga (Phaladeepika ch.6; Saravali)
    adhi = [p for p in BENEFICS if house_from(M, chart.sign[p]) in (6, 7, 8)]
    if adhi:
        weak = [] if len(adhi) == 3 else [f"only {len(adhi)}/3 benefics - partial Adhi yoga"]
        weak += sum((_afflictions(chart, p, comb, losers) for p in adhi), [])
        Y.append(_y("Adhi (Chandra-Adhi)", "Lunar", adhi, [f"{adhi} in 6/7/8 from Moon"], [],
                    "Phaladeepika ch.6; Saravali", "leadership, ministership, comfort, longevity", weak))

    # ---- Amala (Phaladeepika ch.6)
    am = [p for p in BENEFICS if chart.house[p] == 10 or house_from(M, chart.sign[p]) == 10]
    if am:
        Y.append(_y("Amala", "Reputation", am, [f"{am} in 10th from lagna or Moon"], [],
                    "Phaladeepika ch.6", "spotless reputation, ethical conduct, prosperity"))

    # ---- Shakata (BPHS / Phaladeepika) with cancellation
    hm = house_from(chart.sign["Jupiter"], M)
    if hm in (6, 8, 12):
        canc = []
        if chart.house["Moon"] in (1, 4, 7, 10):
            canc.append("Moon in kendra from lagna (Phaladeepika ch.6)")
        Y.append(_y("Shakata", "Dosha-yoga", ["Moon", "Jupiter"], [f"Moon {hm} from Jupiter"], canc,
                    "Phaladeepika ch.6; Saravali", "ups and downs of fortune like a cart wheel"))

    # ---- Vasumati
    vs = [p for p in BENEFICS if chart.house[p] in (3, 6, 10, 11) or house_from(M, chart.sign[p]) in (3, 6, 10, 11)]
    if len(vs) >= 2:
        Y.append(_y("Vasumati", "Wealth", vs, [f"benefics {vs} in upachaya from lagna/Moon"], [],
                    "Phaladeepika ch.6", "steady accumulation of wealth"))

    # ---- Raja yogas (BPHS 39): kendra lord connected with trikona lord
    seen = set()
    for k in (1, 4, 7, 10):
        for t in (5, 9):
            a, b = chart.lord_of_house(k), chart.lord_of_house(t)
            if a == b:
                if k != 1:
                    key = ("self", a)
                    if key not in seen:
                        seen.add(key)
                        Y.append(_y(f"Yogakaraka {a}", "Raja", [a], [f"{a} owns kendra {k} and trikona {t}"], [],
                                    "BPHS ch.34", "a single planet that gives raja yoga in its dasha",
                                    _afflictions(chart, a, comb, losers)))
                continue
            ways = chart.connected(a, b)
            if not ways:
                continue
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            weak = _afflictions(chart, a, comb, losers) + _afflictions(chart, b, comb, losers)
            for x in (a, b):
                bad = [h for h in chart.houses_owned(x) if h in (6, 8, 12)]
                if bad and not set(chart.houses_owned(x)) & {1}:
                    weak.append(f"{x} also owns dusthana {bad} (BPHS ch.39: raja yoga gives mixed results)")
            label = "Dharma-Karmadhipati" if {k, t} == {10, 9} else "Raja yoga"
            Y.append(_y(label, "Raja", [a, b], [f"lord of {k} ({a}) and lord of {t} ({b}): {', '.join(ways)}"], [],
                        "BPHS ch.39", "rise in status, authority, success - timed by dashas of these planets",
                        weak))

    # ---- Dhana yogas (BPHS 41): lords of 2, 11 with 1, 5, 9
    dh = set()
    for x in (2, 11):
        for y in (1, 5, 9):
            a, b = chart.lord_of_house(x), chart.lord_of_house(y)
            if a != b and chart.connected(a, b):
                k = tuple(sorted((a, b)))
                if k not in dh:
                    dh.add(k)
                    Y.append(_y("Dhana yoga", "Wealth", [a, b],
                                [f"lord {x} ({a}) with lord {y} ({b}): {', '.join(chart.connected(a, b))}"], [],
                                "BPHS ch.41", "wealth accumulation in the periods of these planets",
                                _afflictions(chart, a, comb, losers) + _afflictions(chart, b, comb, losers)))

    # ---- Viparita Raja yogas (BPHS 39 / Uttara Kalamrita)
    vip = {6: "Harsha", 8: "Sarala", 12: "Vimala"}
    for h, n in vip.items():
        lord = chart.lord_of_house(h)
        if chart.house[lord] in (6, 8, 12):
            canc = []
            if 1 in chart.houses_owned(lord):
                canc.append(f"{lord} is also lagna lord - its placement in a dusthana harms the self")
            good_conj = [q for q in chart.conjunct(lord)
                         if not set(chart.houses_owned(q)) <= {6, 8, 12} and q not in ("Rahu", "Ketu")]
            weak = [f"{lord} joined by non-dusthana lords {good_conj} - mixes results"] if good_conj else []
            other = [x for x in chart.houses_owned(lord) if x not in (6, 8, 12)]
            if other:
                weak.append(f"{lord} also owns house(s) {other}; those houses suffer from the dusthana placement")
            Y.append(_y(f"{n} (Viparita Raja)", "Viparita", [lord],
                        [f"{h}th lord {lord} in house {chart.house[lord]}"], canc,
                        "BPHS ch.39; Uttara Kalamrita", "success arising out of adversity / others' loss", weak))

    # ---- Parivartana (exchange) yogas (Phaladeepika ch.6)
    done = set()
    for p in SEVEN:
        q = SIGN_LORD[chart.sign[p]]
        if q != p and q in SEVEN and SIGN_LORD[chart.sign[q]] == p and (q, p) not in done:
            done.add((p, q))
            hs = {chart.house[p], chart.house[q]}
            kind = "Dainya" if hs & {6, 8, 12} else "Khala" if 3 in hs else "Maha"
            res = {"Maha": "great prosperity and status", "Dainya": "struggles, enemies, fluctuations",
                   "Khala": "fluctuating fortune; courage-driven gains"}[kind]
            Y.append(_y(f"{kind} Parivartana", "Exchange", [p, q], [f"{p} and {q} exchange signs (houses {sorted(hs)})"],
                        [], "Phaladeepika ch.6", res))

    # ---- Neecha Bhanga (Phaladeepika ch.7; BPHS)
    for p in SEVEN:
        if chart.dig[p] != "Debilitated":
            continue
        s = chart.sign[p]
        disp = SIGN_LORD[s]
        ex_lord = SIGN_LORD[exalt_sign(p)]
        exalted_here = [q for q in SEVEN if EXALTATION[q][0] == s]
        conds = []
        if _kendra_from(chart, disp, L) or _kendra_from(chart, disp, M):
            conds.append(f"dispositor {disp} in kendra from lagna/Moon (Phaladeepika ch.7) [strong]")
        if _kendra_from(chart, ex_lord, L) or _kendra_from(chart, ex_lord, M):
            conds.append(f"lord of exaltation sign {ex_lord} in kendra from lagna/Moon (Phaladeepika ch.7) [strong]")
        for q in exalted_here:
            if _kendra_from(chart, q, L) or _kendra_from(chart, q, M):
                conds.append(f"{q} (exalted in {SIGNS[s]}) in kendra from lagna/Moon (Phaladeepika ch.7) [strong]")
        if disp in chart.planet_aspected_by(p):
            conds.append(f"dispositor {disp} aspects {p} (Saravali) [medium]")
        if disp in chart.conjunct(p) or any(q in chart.conjunct(p) for q in exalted_here):
            conds.append("conjunct dispositor or the planet exalted in that sign [medium]")
        if chart.vargas[9][p] == exalt_sign(p):
            conds.append(f"{p} exalted in navamsa (Jataka Parijata) [medium]")
        if chart.retro(p):
            conds.append(f"{p} retrograde - some authors treat as strong (disputed) [weak]")
        if _kendra_from(chart, p, L):
            conds.append(f"debilitated planet itself in kendra from lagna [weak, popular]")
        strong = sum("[strong]" in c for c in conds)
        verdict = ("Neecha Bhanga Raja Yoga (strong cancellation)" if strong >= 2 else
                   "Neecha Bhanga (cancelled debility)" if conds else "Debility NOT cancelled")
        Y.append({"name": f"Neecha Bhanga check: {p}", "category": "Debility", "planets": [p],
                  "conditions": conds or ["none of the cancellation conditions are met"], "cancellations": [],
                  "weakenings": [], "verdict": verdict, "source": "Phaladeepika ch.7; BPHS; Saravali; Jataka Parijata",
                  "result": "a cancelled debility often gives a rise after initial struggle; an uncancelled one "
                            "gives weak results for that planet's significations and houses"})

    # ---- Saraswati (Phaladeepika ch.6)
    good = [1, 2, 4, 5, 7, 9, 10]
    if all(chart.house[p] in good for p in ("Jupiter", "Venus", "Mercury")) and \
            chart.dig["Jupiter"] in ("Exalted", "Own", "Moolatrikona", "Friend", "Great Friend"):
        Y.append(_y("Saraswati", "Learning", ["Jupiter", "Venus", "Mercury"],
                    ["Jupiter, Venus, Mercury in kendra/trikona/2nd; Jupiter strong"], [],
                    "Phaladeepika ch.6", "learning, eloquence, poetry, fame in scholarship"))

    # ---- Lakshmi (BPHS 41)
    l9 = chart.lord_of_house(9)
    if chart.house[l9] in (1, 4, 5, 7, 9, 10) and chart.dig[l9] in ("Exalted", "Own", "Moolatrikona") and \
            shad["planets"].get(chart.lord_of_house(1), {"ratio": 1})["ratio"] >= 1:
        Y.append(_y("Lakshmi", "Wealth", [l9], [f"9th lord {l9} {chart.dig[l9]} in kendra/trikona, lagna lord strong"],
                    [], "BPHS ch.41", "wealth, nobility, fortune"))

    # ---- Kartari (hemming) of lagna and Moon
    for ref, name in ((L, "Lagna"), (M, "Moon")):
        b12 = [p for p in PLANETS if house_from(ref, chart.sign[p]) == 12 and p != "Moon"]
        b2 = [p for p in PLANETS if house_from(ref, chart.sign[p]) == 2 and p != "Moon"]
        if b12 and b2:
            if all(p in BENEFICS for p in b12 + b2):
                Y.append(_y(f"Shubha Kartari ({name})", "Kartari", b12 + b2, [f"{name} hemmed by benefics"], [],
                            "Phaladeepika ch.6", "protection, health, prosperity for that point"))
            elif all(p in MALEFICS for p in b12 + b2):
                Y.append(_y(f"Papa Kartari ({name})", "Kartari", b12 + b2, [f"{name} hemmed by malefics"], [],
                            "Phaladeepika ch.6", "pressure, obstacles and health issues for that point"))

    # ---- Mahabhagya (BPHS / Phaladeepika)
    day = chart.sun["is_day"]
    odd = all(s % 2 == 0 for s in (L, chart.sign["Sun"], M))
    even = all(s % 2 == 1 for s in (L, chart.sign["Sun"], M))
    g = chart.birth.gender
    if (g == "M" and day and odd) or (g == "F" and not day and even):
        Y.append(_y("Mahabhagya", "Fortune", ["Sun", "Moon"],
                    ["day birth with Lagna/Sun/Moon in odd signs (male) or night birth with even signs (female)"], [],
                    "BPHS; Phaladeepika ch.6", "great fortune, long life, fame"))

    # ---- Sankhya (Nabhasa) yogas by number of signs occupied (BPHS 35)
    occ = len({chart.sign[p] for p in SEVEN})
    sank = {7: "Vallaki/Veena", 6: "Dama", 5: "Pasha", 4: "Kedara", 3: "Shoola", 2: "Yuga", 1: "Gola"}
    sres = {7: "many friends, arts, happiness", 6: "generous, helpful, wealthy", 5: "skilled earner, many dependants",
            4: "agriculture/land, useful to others", 3: "sharp, may be harsh, struggles",
            2: "unconventional, may lack wealth", 1: "poverty or extreme focus"}
    Y.append(_y(f"{sank[occ]} (Sankhya Nabhasa)", "Nabhasa", list(SEVEN), [f"7 planets occupy {occ} signs"], [],
                "BPHS ch.35", sres[occ] + " (Nabhasa yogas give a background tone, not specific events)"))

    # ---- Chatussagara
    if all(chart.occupants(h) for h in (1, 4, 7, 10)):
        Y.append(_y("Chatussagara", "Fame", [], ["all four kendras occupied"], [], "Phaladeepika ch.6",
                    "fame across the four seas, wealth, longevity"))
    return Y
