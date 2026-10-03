"""Life-area analysis and event timing by multiple confirmation.

Promise (does the chart promise the event?) is judged from the house, its lord, the karaka, the
divisional chart and ashtakavarga. Timing then needs ALL of:
  1. a dasha / antardasha whose lords signify the area (occupant, lord, aspect, karaka, nakshatra link)
  2. Jupiter and Saturn both influencing the house or its lord by transit (double transit)
  3. supporting ashtakavarga bindus in the transited sign
Windows are scored by how many independent factors agree; nothing is predicted from one factor.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import dasha as D
from . import ephemeris as eph
from .chart import nakshatra_of
from .constants import BHAVA_KARAKA, NATURAL_BENEFICS, PLANETS, SIGN_LORD, SIGNS, house_from
from .dignity import DIGNITY_SCORE, dignity
from .transits import _influenced_houses, slow_positions

AREAS = {
    "marriage": {"houses": [7, 2, 11], "main": 7, "karaka_m": "Venus", "karaka_f": "Jupiter", "varga": 9,
                 "label": "Marriage / spouse"},
    "career": {"houses": [10, 6, 11], "main": 10, "karaka": "Saturn", "varga": 10, "label": "Career / job / status"},
    "wealth": {"houses": [2, 11, 5, 9], "main": 11, "karaka": "Jupiter", "varga": 2, "label": "Money / gains"},
    "children": {"houses": [5, 2, 11], "main": 5, "karaka": "Jupiter", "varga": 7, "label": "Children"},
    "education": {"houses": [4, 5, 9], "main": 5, "karaka": "Mercury", "varga": 24, "label": "Education"},
    "property": {"houses": [4, 11, 2], "main": 4, "karaka": "Mars", "varga": 4, "label": "Property / home / vehicle"},
    "foreign": {"houses": [12, 9, 7, 3], "main": 12, "karaka": "Rahu", "varga": 1, "label": "Foreign travel / settlement"},
    "health": {"houses": [1, 6, 8, 12], "main": 1, "karaka": "Sun", "varga": 1,
               "label": "Health crises (6/8/12, marakas)", "adverse": True},
    "father": {"houses": [9, 10], "main": 9, "karaka": "Sun", "varga": 12, "label": "Father"},
    "mother": {"houses": [4], "main": 4, "karaka": "Moon", "varga": 12, "label": "Mother"},
    "siblings": {"houses": [3, 11], "main": 3, "karaka": "Mars", "varga": 3, "label": "Siblings"},
    "mind": {"houses": [4, 1, 5, 8], "main": 4, "karaka": "Moon", "varga": 1,
             "label": "Mind / emotional stability (Moon, 4th, 5th)", "adverse": False},
    "govt_authority": {"houses": [10, 9, 1, 11], "main": 10, "karaka": "Sun", "varga": 10,
                       "label": "Government job / authority / fame"},
    "accidents_surgery": {"houses": [8, 6, 1], "main": 8, "karaka": "Mars", "varga": 1,
                          "label": "Accidents / surgery / sudden events", "adverse": True},
    "spirituality": {"houses": [9, 12, 5], "main": 12, "karaka": "Ketu", "varga": 20, "label": "Spiritual growth"},
    "litigation": {"houses": [6, 8, 12], "main": 6, "karaka": "Mars", "varga": 1, "label": "Disputes / debts / enemies",
                   "adverse": True},
}


def _karaka(chart, spec) -> str:
    if "karaka_m" in spec:
        return spec["karaka_f"] if chart.birth.gender == "F" else spec["karaka_m"]
    return spec["karaka"]


def significators(chart, houses: list[int]) -> dict[str, list[str]]:
    """Planets connected to the given houses, with the reason. Order of strength follows classical practice:
    occupant > lord > aspecting > in nakshatra of occupant/lord > conjunct lord."""
    sig: dict[str, list[str]] = {}

    def add(p, why):
        sig.setdefault(p, [])
        if why not in sig[p]:
            sig[p].append(why)

    for h in houses:
        lord = chart.lord_of_house(h)
        add(lord, f"lord of {h}")
        for p in chart.occupants(h):
            add(p, f"occupies {h}")
        for p in chart.aspected_by(h, primary_only=True):
            add(p, f"aspects {h}")
        for p in chart.conjunct(lord):
            add(p, f"with lord of {h}")
    core = list(sig)
    for p in PLANETS:
        nl = nakshatra_of(chart.lon[p])["lord"]
        if nl in core and p not in sig:
            add(p, f"in nakshatra of {nl}")
    for node in ("Rahu", "Ketu"):  # nodes act for their dispositor
        disp = SIGN_LORD[chart.sign[node]]
        if disp in core:
            add(node, f"dispositor {disp} is a significator")
    return sig


def promise(chart, area: str, av: dict, cond: dict) -> dict:
    spec = AREAS[area]
    h = spec["main"]
    lord = chart.lord_of_house(h)
    kar = _karaka(chart, spec)
    plus, minus = [], []
    occ = chart.occupants(h)
    for p in occ:
        (plus if p in NATURAL_BENEFICS else minus).append(f"{p} occupies house {h}")
    for p in chart.aspected_by(h, primary_only=True):
        if p not in occ:
            (plus if p in NATURAL_BENEFICS else minus).append(f"{p} aspects house {h}")
    ds = DIGNITY_SCORE.get(chart.dig[lord], 0)
    (plus if ds > 0 else minus).append(f"house lord {lord} is {chart.dig[lord]} in house {chart.house[lord]}")
    if chart.house[lord] in (6, 8, 12) and h not in (6, 8, 12):
        minus.append(f"house lord {lord} sits in dusthana {chart.house[lord]}")
    if chart.house[lord] in (1, 4, 5, 7, 9, 10):
        plus.append(f"house lord {lord} in kendra/trikona")
    kn = cond[kar]["net"]
    (plus if kn >= 0 else minus).append(f"karaka {kar}: {len(cond[kar]['strengths'])} strengths vs "
                                        f"{len(cond[kar]['weaknesses'])} weaknesses")
    sav = av["sav"][(chart.lagna + h - 1) % 12]
    if sav >= 28:
        plus.append(f"SAV bindus in house {h}: {sav} (good)")
    elif sav < 25:
        minus.append(f"SAV bindus in house {h}: {sav} (weak)")
    d = spec["varga"]
    if d != 1:
        vs = chart.vargas[d][lord]
        vd = dignity(lord, vs, 0, chart.d1_signs, use_mt=False)
        (plus if DIGNITY_SCORE.get(vd, 0) > 0 else minus).append(f"in D{d}, house lord {lord} is in {SIGNS[vs]} ({vd})")
        vl = chart.vargas[d]["Lagna"]
        vh = house_from(vl, vs)
        (minus if vh in (6, 8, 12) else plus).append(f"in D{d}, house lord falls in house {vh} from D{d} lagna")
        kvs = chart.vargas[d][kar]
        kd = dignity(kar, kvs, 0, chart.d1_signs, use_mt=False)
        (plus if DIGNITY_SCORE.get(kd, 0) > 0 else minus).append(f"in D{d}, karaka {kar} is {kd}")
    # same house from Moon
    hm = (chart.moon_sign + h - 1) % 12
    mal_m = [p for p in PLANETS if chart.sign[p] == hm and p not in NATURAL_BENEFICS]
    if mal_m:
        minus.append(f"malefics {mal_m} in house {h} from Moon")
    score = len(plus) - len(minus)
    adverse = spec.get("adverse", False)
    verdict = ("strong" if score >= 3 else "moderate" if score >= 0 else "weak" if score >= -3 else "very weak")
    if adverse:
        verdict = f"{verdict} protection" if score >= 0 else f"{verdict} protection - vulnerable area"
    return {"area": spec["label"], "house": h, "lord": lord, "karaka": kar, "favourable": plus,
            "unfavourable": minus, "score": score, "verdict": verdict}


def event_windows(chart, area: str, start: datetime, end: datetime, top: int = 8) -> dict:
    spec = AREAS[area]
    houses = spec["houses"]
    main = spec["main"]
    sig = significators(chart, houses)
    main_sig = significators(chart, [main])
    kar = _karaka(chart, spec)
    v = D.vimshottari(chart.lon["Moon"], chart.utc, chart.settings["dasha_year"])
    lord = chart.lord_of_house(main)
    lord_sign = chart.sign[lord]
    main_sign = (chart.lagna + main - 1) % 12

    def weight(p):
        w = 0.0
        if p in main_sig:
            w += 2.0
        elif p in sig:
            w += 1.0
        if p == kar:
            w += 1.0
        return w

    from .ashtakavarga import compute as avc
    jup_bav = avc(chart.sign, chart.lagna)["bav"]["Jupiter"][main_sign]
    windows = []
    for per in D.periods_between(v, start, end):
        wm, wa = weight(per["md"]), weight(per["ad"])
        if wm + wa < 2 or wa == 0 and wm < 3:
            continue
        a, b = max(per["start"], start), min(per["end"], end)
        t = a
        while t < b:  # scan each month of the antardasha for double transit
            jd = eph.julday(t.astimezone(timezone.utc))
            pos = slow_positions(jd, chart.settings)
            jh = _influenced_houses(chart.lagna, pos["Jupiter"], "Jupiter")
            sh = _influenced_houses(chart.lagna, pos["Saturn"], "Saturn")
            lord_h = house_from(chart.lagna, lord_sign)
            dt_house = main in jh and main in sh
            dt_lord = lord_h in jh and lord_h in sh
            factors = [f"MD {per['md']} ({', '.join(sig.get(per['md'], ['karaka'] if per['md'] == kar else []))})",
                       f"AD {per['ad']} ({', '.join(sig.get(per['ad'], ['karaka'] if per['ad'] == kar else []))})"]
            score = wm + wa
            run = D.running(v, t)
            if run and weight(run["pd"]["lord"]) > 0:
                score += 0.5 * weight(run["pd"]["lord"])
                factors.append(f"PD {run['pd']['lord']} also a significator")
            if dt_house:
                score += 2
                factors.append(f"double transit (Jupiter+Saturn) on house {main}")
            if dt_lord:
                score += 1.5
                factors.append(f"double transit on house of lord {lord} ({lord_h})")
            jsign = pos["Jupiter"]
            if house_from(chart.lagna, jsign) == main or jsign == lord_sign:
                score += 1
                factors.append("Jupiter transits the house or its lord's sign")
            jb = jup_bav
            if jb >= 5:
                score += 0.5
                factors.append(f"Jupiter BAV {jb} bindus in house {main}")
            windows.append({"start": t, "md": per["md"], "ad": per["ad"], "score": round(score, 1),
                            "factors": factors, "double_transit": dt_house or dt_lord})
            t += timedelta(days=30)
    # merge consecutive months with the same MD/AD and transit state into one range (keep the peak month)
    merged = []
    for w in windows:
        last = merged[-1] if merged else None
        if last and last["md"] == w["md"] and last["ad"] == w["ad"] and \
                last["double_transit"] == w["double_transit"] and (w["start"] - last["end"]).days <= 31:
            last["end"] = w["start"] + timedelta(days=30)
            if w["score"] > last["score"]:
                last["score"], last["factors"], last["peak"] = w["score"], w["factors"], w["start"]
        else:
            merged.append({**w, "end": w["start"] + timedelta(days=30), "peak": w["start"]})
    for m in merged:
        m["confidence"] = ("high (dasha + double transit + support)" if m["double_transit"] and m["score"] >= 6 else
                           "medium" if m["double_transit"] or m["score"] >= 5 else "low (dasha only)")
    ranked = sorted(merged, key=lambda w: (-w["score"], w["start"]))[:top]
    for r in ranked:
        r["start"], r["end"], r["peak"] = (r[k].strftime("%Y-%m") for k in ("start", "end", "peak"))
    return {"area": spec["label"], "significators": sig, "karaka": kar, "windows": ranked,
            "method": "score = dasha significance (MD+AD) + Jupiter/Saturn double transit on house and lord + "
                      "Jupiter transit + ashtakavarga. A window is 'high' only when dasha AND double transit agree."}


def maraka_periods(chart, start: datetime, end: datetime) -> list[dict]:
    """Periods of maraka lords (lords/occupants of 2 and 7, plus 8th/12th lords as secondary) - BPHS ch.44.
    These are health-vigilance windows, not death predictions."""
    primary = {chart.lord_of_house(2), chart.lord_of_house(7)} | set(chart.occupants(2)) | set(chart.occupants(7))
    secondary = {chart.lord_of_house(8), chart.lord_of_house(12), chart.lord_of_house(6)}
    v = D.vimshottari(chart.lon["Moon"], chart.utc, chart.settings["dasha_year"])
    out = []
    for per in D.periods_between(v, start, end):
        tags = []
        for role, lordp in (("MD", per["md"]), ("AD", per["ad"])):
            if lordp in primary:
                tags.append(f"{role} {lordp} = maraka")
            elif lordp in secondary:
                tags.append(f"{role} {lordp} = 6/8/12 lord")
        if len(tags) == 2:
            out.append({"md": per["md"], "ad": per["ad"], "start": D.fmt(per["start"]), "end": D.fmt(per["end"]),
                        "why": tags})
    return out


def rectification_sensitivity(chart_factory, birth, minutes: int = 30) -> dict:
    """How much the conclusions depend on the birth time: scan +/- minutes and report when key
    points (lagna, D9 lagna, D10 lagna, Moon nakshatra pada, dasha lord at birth) change."""
    base = chart_factory(birth)
    keys = lambda c: {"Lagna": SIGNS[c.lagna], "D9 Lagna": SIGNS[c.vargas[9]["Lagna"]],
                      "D10 Lagna": SIGNS[c.vargas[10]["Lagna"]], "D7 Lagna": SIGNS[c.vargas[7]["Lagna"]],
                      "D60 Lagna": SIGNS[c.vargas[60]["Lagna"]],
                      "Moon pada": f"{nakshatra_of(c.lon['Moon'])['name']}-{nakshatra_of(c.lon['Moon'])['pada']}"}
    b0 = keys(base)
    changes = {k: [] for k in b0}
    from dataclasses import replace
    for m in list(range(-minutes, 0)) + list(range(1, minutes + 1)):
        c = chart_factory(replace(birth, dt_local=birth.dt_local + timedelta(minutes=m)))
        for k, v in keys(c).items():
            if v != b0[k]:
                changes[k].append(m)
    out = {}
    for k, ms in changes.items():
        before = [m for m in ms if m < 0]
        after = [m for m in ms if m > 0]
        out[k] = {"value": b0[k],
                  "stable_from_minutes": max(before) + 1 if before else -minutes,
                  "stable_to_minutes": min(after) - 1 if after else minutes}
        span = out[k]["stable_to_minutes"] - out[k]["stable_from_minutes"]
        out[k]["reliability"] = ("reliable" if span >= 2 * minutes else "time-sensitive" if span > 8 else
                                 "highly time-sensitive - verify birth time")
    return {"window_minutes": minutes, "points": out,
            "limits": "Rectification can only narrow the time using known life events; with an uncertain time, "
                      "D9 within a few minutes and D60 within seconds are unreliable, and so are judgements that "
                      "rest on them."}


def rectify_by_events(chart_factory, birth, events: list[dict], minutes: int = 60, step: int = 2) -> list[dict]:
    """Score candidate birth times by how well the running MD/AD at each known event signify that event.
    events: [{"area": "marriage", "date": "2015-02-10"}, ...]"""
    from dataclasses import replace
    res = []
    for m in range(-minutes, minutes + 1, step):
        b = replace(birth, dt_local=birth.dt_local + timedelta(minutes=m))
        c = chart_factory(b)
        v = D.vimshottari(c.lon["Moon"], c.utc, c.settings["dasha_year"])
        score, detail = 0.0, []
        for ev in events:
            when = datetime.fromisoformat(ev["date"]).replace(tzinfo=timezone.utc)
            run = D.running(v, when)
            if not run:
                continue
            sig = significators(c, AREAS[ev["area"]]["houses"])
            main = significators(c, [AREAS[ev["area"]]["main"]])
            s = sum((2 if run[k]["lord"] in main else 1 if run[k]["lord"] in sig else 0) for k in ("md", "ad", "pd"))
            score += s
            detail.append(f"{ev['area']} {ev['date']}: {run['md']['lord']}/{run['ad']['lord']}/{run['pd']['lord']} -> {s}")
        res.append({"offset_minutes": m, "time": b.dt_local.strftime("%H:%M"), "lagna": SIGNS[c.lagna],
                    "d9_lagna": SIGNS[c.vargas[9]["Lagna"]], "score": score, "detail": detail})
    return sorted(res, key=lambda r: (-r["score"], abs(r["offset_minutes"])))[:10]
