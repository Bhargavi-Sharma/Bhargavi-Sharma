"""Astronomical positions via the Swiss Ephemeris (built-in Moshier model, ~1 arcsec)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from .constants import PLANETS, WEEKDAY_LORD, HORA_ORDER

AYANAMSA = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
    "true_chitra": swe.SIDM_TRUE_CITRA,
}

_IDS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
_EPH = swe.FLG_MOSEPH


@dataclass
class Body:
    name: str
    lon: float          # sidereal longitude
    lat: float          # ecliptic latitude
    speed: float        # deg/day in longitude
    decl: float         # declination (tropical equator)

    @property
    def retro(self) -> bool:
        return self.speed < 0


@dataclass
class Snapshot:
    """Planet positions at one instant, plus local angles when a place is known."""
    jd_ut: float
    ayanamsa: float
    bodies: dict[str, Body]
    asc: float | None = None
    mc: float | None = None
    extra: dict = field(default_factory=dict)


def to_utc(local: datetime, tz: str | float) -> datetime:
    """Convert a naive local datetime using an IANA zone name or a UTC offset in hours."""
    if isinstance(tz, (int, float)):
        aware = local.replace(tzinfo=timezone(timedelta(hours=float(tz))))
    else:
        aware = local.replace(tzinfo=ZoneInfo(tz))
    return aware.astimezone(timezone.utc)


def julday(utc: datetime) -> float:
    h = utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3.6e9
    return swe.julday(utc.year, utc.month, utc.day, h)


def jd_to_utc(jd: float) -> datetime:
    y, m, d, h = swe.revjul(jd)
    return datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)


def snapshot(jd_ut: float, settings: dict, lat: float | None = None, lon: float | None = None) -> Snapshot:
    swe.set_sid_mode(AYANAMSA[settings["ayanamsa"]])
    flags = _EPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    bodies: dict[str, Body] = {}
    for name, pid in _IDS.items():
        (plon, plat, _, sp, _, _), _ = swe.calc_ut(jd_ut, pid, flags)
        (_, dec, _, _, _, _), _ = swe.calc_ut(jd_ut, pid, _EPH | swe.FLG_EQUATORIAL)
        bodies[name] = Body(name, plon, plat, sp, dec)
    node = swe.TRUE_NODE if settings["node_type"] == "true" else swe.MEAN_NODE
    (nlon, _, _, nsp, _, _), _ = swe.calc_ut(jd_ut, node, flags)
    bodies["Rahu"] = Body("Rahu", nlon % 360, 0.0, nsp, 0.0)
    bodies["Ketu"] = Body("Ketu", (nlon + 180) % 360, 0.0, nsp, 0.0)
    snap = Snapshot(jd_ut, swe.get_ayanamsa_ut(jd_ut), {p: bodies[p] for p in PLANETS})
    if lat is not None and lon is not None:
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b"W", swe.FLG_SIDEREAL)
        snap.asc, snap.mc = ascmc[0] % 360, ascmc[1] % 360
    return snap


def sun_events(jd_ut: float, lat: float, lon: float) -> dict:
    """Sunrise before the birth moment, and the following sunset and sunrise (Vedic day = sunrise to sunrise)."""
    geo = (lon, lat, 0)
    rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    ssmi = swe.CALC_SET | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION

    def nxt(start, flag):
        res, t = swe.rise_trans(start, swe.SUN, flag, geo, 0, 0, _EPH)
        return t[0] if res == 0 else None

    rise = nxt(jd_ut - 1.0, rsmi)
    while rise is not None and rise + 1.0 <= jd_ut:
        nr = nxt(rise + 0.01, rsmi)
        if nr is None or nr > jd_ut:
            break
        rise = nr
    if rise is None:  # polar day/night: fall back to 6am/6pm local mean time
        local_noon = jd_ut - ((jd_ut + 0.5 + lon / 360) % 1) + 0.5
        rise = local_noon - 0.25
    set_ = nxt(rise + 0.01, ssmi) or rise + 0.5
    next_rise = nxt(rise + 0.5, rsmi) or rise + 1.0
    is_day = rise <= jd_ut < set_
    weekday = int((rise + 1.5 + lon / 360) % 7)  # Sunday = 0, using the local date of the sunrise
    # hora: day and night each divided into 12 unequal horas starting from the weekday lord
    if is_day:
        idx = int((jd_ut - rise) / ((set_ - rise) / 12))
    else:
        idx = 12 + int((jd_ut - set_) / ((next_rise - set_) / 12))
    start = HORA_ORDER.index(WEEKDAY_LORD[weekday])
    hora_lord = HORA_ORDER[(start + idx) % 7]
    return {"sunrise": rise, "sunset": set_, "next_sunrise": next_rise, "is_day": is_day,
            "weekday": weekday, "vara_lord": WEEKDAY_LORD[weekday], "hora_lord": hora_lord}
