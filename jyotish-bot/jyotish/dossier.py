"""Assembles every computed factor into one JSON-serialisable report (the 'dossier').

The chat layer is only allowed to reason from this dossier (plus tool calls into the same
engine), so the same chart always produces the same facts.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import ashtakavarga, dasha as D, doshas, functional, jaimini, profiles, remedies, shadbala, timing, transits, yogas
from .chart import BirthData, Chart, nakshatra_of
from .constants import PLANETS, SIGNS
from .variants import VARIANTS
from .vargas import ALL_VARGAS, VARGA_NAMES


def _age(chart, ym: str) -> float:
    y, m = map(int, ym.split("-")[:2])
    return round(y + (m - 1) / 12 - (chart.birth.dt_local.year + (chart.birth.dt_local.month - 1) / 12), 1)


def build(birth: BirthData, settings: dict | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    c = Chart(birth, settings)
    av = ashtakavarga.compute(c.sign, c.lagna)
    shad = shadbala.compute(c)
    comb = functional.combustion(c)
    war = shadbala.planetary_war(c)
    func = functional.functional_nature(c)
    cond = functional.planet_condition(c, comb, war, shad, func)
    v = D.vimshottari(c.lon["Moon"], c.utc, c.settings["dasha_year"])
    run = D.running(v, now)

    # dasha table: every MD, with antardashas for all of them (compact)
    md_rows = []
    for md in v["mahadashas"]:
        md_rows.append({"lord": md["lord"], "start": D.fmt(md["start"]), "end": D.fmt(md["end"]),
                        "age_start": round((md["start"] - c.utc).days / 365.25, 1),
                        "antardashas": [{"lord": a["lord"], "start": D.fmt(a["start"]), "end": D.fmt(a["end"])}
                                        for a in D.antardashas(md)]})
    current = {}
    if run:
        current = {"mahadasha": run["md"]["lord"], "md_ends": D.fmt(run["md"]["end"]),
                   "antardasha": run["ad"]["lord"], "ad_ends": D.fmt(run["ad"]["end"]),
                   "pratyantar": run["pd"]["lord"], "pd_ends": D.fmt(run["pd"]["end"])}

    birth_utc = c.utc
    win_start = max(birth_utc + timedelta(days=365.25 * 16), birth_utc)
    win_end = now + timedelta(days=365.25 * 30)
    areas = {}
    for area in timing.AREAS:
        pr = timing.promise(c, area, av, cond)
        ew = timing.event_windows(c, area, win_start, win_end)
        for w in ew["windows"]:
            w["age_at_start"] = _age(c, w["start"])
            w["is_past"] = w["end"] < now.strftime("%Y-%m")
        areas[area] = {"promise": pr, "timing": ew}

    vargas = {}
    for d in ALL_VARGAS:
        vargas[f"D{d}"] = {"meaning": VARGA_NAMES[d], "Lagna": SIGNS[c.vargas[d]["Lagna"]],
                           **{p: SIGNS[c.vargas[d][p]] for p in PLANETS}}

    jai = jaimini.report(c)
    age_now = round((now - birth_utc).days / 365.25, 1)
    lg = jai["longevity"]
    upper = {"Short (Alpa)": 36, "Medium (Madhya)": 72, "Long (Purna)": 120}[lg["category"]]
    lg["age_now"] = age_now
    if age_now > upper:
        lg["reality_check"] = (f"Native is already {age_now}, beyond the {lg['category']} range - this Jaimini "
                               "indicator has not worked for this chart; do not lean on it.")

    moon_nak = nakshatra_of(c.lon["Moon"])
    return {
        "input": {"name": birth.name, "local_time": birth.dt_local.isoformat(), "timezone": str(birth.tz),
                  "place": birth.place, "lat": birth.lat, "lon": birth.lon, "gender": birth.gender,
                  "utc": birth_utc.isoformat(), "julian_day": round(c.jd, 6)},
        "settings": {k: c.settings[k] for k in ("ayanamsa", "node_type", "dasha_year", "chara_karaka_count")},
        "ayanamsa_value": round(c.snap.ayanamsa, 5),
        "generated_for_date": now.strftime("%Y-%m-%d"),
        "lagna": c.lagna_row(),
        "moon": {"sign": SIGNS[c.moon_sign], "nakshatra": moon_nak["name"], "pada": moon_nak["pada"],
                 "nakshatra_lord": moon_nak["lord"], "gana": moon_nak["gana"], "deity": moon_nak["deity"],
                 "paksha": "Shukla (waxing)" if (c.lon["Moon"] - c.lon["Sun"]) % 360 < 180 else "Krishna (waning)",
                 "tithi": int(((c.lon["Moon"] - c.lon["Sun"]) % 360) // 12) + 1},
        "birth_day": {"weekday_lord": c.sun["vara_lord"], "hora_lord": c.sun["hora_lord"],
                      "day_birth": c.sun["is_day"]},
        "planets": [c.planet_row(p) for p in PLANETS],
        "houses": c.house_rows(),
        "bhava_chalit_shifts": c.bhava_chalit(),
        "vargas": vargas,
        "functional_nature": func,
        "combustion": comb,
        "planetary_war": war,
        "gandanta": functional.gandanta(c),
        "planet_condition": cond,
        "shadbala": shad,
        "ashtakavarga": {"bav_by_sign": {p: dict(zip(SIGNS, r)) for p, r in av["bav"].items()},
                         "sav_by_house": ashtakavarga.interpret_sav(av["sav"], c.lagna)},
        "yogas": yogas.detect(c, comb, war, shad),
        "doshas": doshas.detect(c),
        "jaimini": jai,
        "vimshottari": {"birth_dasha_lord": v["birth_lord"], "balance_at_birth_years": v["balance_years"],
                        "year_length_days": v["year_days"], "current": current, "mahadashas": md_rows},
        "transits_now": transits.transit_report(c, now, av),
        "saturn_cycles": transits.sade_sati_periods(c, birth_utc, years=100),
        "life_areas": areas,
        "profiles": profiles.all_profiles(c),
        "health_vigilance_periods": timing.maraka_periods(c, birth_utc + timedelta(days=365.25 * 18),
                                                          birth_utc + timedelta(days=365.25 * 100)),
        "remedies": {"gemstones": remedies.gem_advice(c, func, cond, shad, comb),
                     "mantra_daan": remedies.mantra_daan(c, func, cond),
                     "lal_kitab": remedies.lal_kitab(c)},
        "birth_time_sensitivity": timing.rectification_sensitivity(lambda b: Chart(b, settings), birth, 30),
        "variants_in_use": {k: {"choice": c.settings.get(k), "note": VARIANTS[k]["note"]} for k in VARIANTS},
    }


def serialise(obj):
    """json.dumps default= hook."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(type(obj))
