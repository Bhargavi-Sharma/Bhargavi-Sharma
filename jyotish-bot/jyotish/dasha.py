"""Vimshottari dasha (BPHS ch.46-47): mahadasha, antardasha, pratyantardasha."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .constants import DASHA_ORDER, DASHA_YEARS, NAK_SPAN

TOTAL = 120


def _seq_from(lord: str) -> list[str]:
    i = DASHA_ORDER.index(lord)
    return DASHA_ORDER[i:] + DASHA_ORDER[:i]


def _sub(lord: str, start: datetime, length_days: float) -> list[dict]:
    out, t = [], start
    for sub in _seq_from(lord):
        d = length_days * DASHA_YEARS[sub] / TOTAL
        out.append({"lord": sub, "start": t, "end": t + timedelta(days=d)})
        t += timedelta(days=d)
    return out


def vimshottari(moon_lon: float, birth_utc: datetime, year_days: float = 365.25) -> dict:
    nak = int(moon_lon // NAK_SPAN) % 27
    lord = DASHA_ORDER[nak % 9]
    frac = (moon_lon % NAK_SPAN) / NAK_SPAN
    elapsed_days = frac * DASHA_YEARS[lord] * year_days
    start = birth_utc - timedelta(days=elapsed_days)  # notional start of the birth mahadasha
    mds, t = [], start
    for md in _seq_from(lord) * 2:  # two cycles covers any lifespan
        length = DASHA_YEARS[md] * year_days
        mds.append({"lord": md, "start": t, "end": t + timedelta(days=length), "length_days": length})
        t += timedelta(days=length)
        if t > birth_utc + timedelta(days=125 * 365.25):
            break
    return {"birth_lord": lord, "balance_years": round(DASHA_YEARS[lord] * (1 - frac), 4),
            "mahadashas": mds, "year_days": year_days}


def antardashas(md: dict) -> list[dict]:
    return _sub(md["lord"], md["start"], md["length_days"])


def pratyantars(md: dict, ad: dict) -> list[dict]:
    length = (ad["end"] - ad["start"]).total_seconds() / 86400
    return _sub(ad["lord"], ad["start"], length)


def running(v: dict, when: datetime) -> dict:
    """Mahadasha / antardasha / pratyantar running at `when`."""
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    for md in v["mahadashas"]:
        if md["start"] <= when < md["end"]:
            for ad in antardashas(md):
                if ad["start"] <= when < ad["end"]:
                    for pd in pratyantars(md, ad):
                        if pd["start"] <= when < pd["end"]:
                            return {"md": md, "ad": ad, "pd": pd}
    return {}


def periods_between(v: dict, a: datetime, b: datetime) -> list[dict]:
    """All MD/AD pairs overlapping [a, b]."""
    out = []
    for md in v["mahadashas"]:
        if md["end"] < a or md["start"] > b:
            continue
        for ad in antardashas(md):
            if ad["end"] < a or ad["start"] > b:
                continue
            out.append({"md": md["lord"], "ad": ad["lord"], "start": ad["start"], "end": ad["end"]})
    return out


def fmt(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")
