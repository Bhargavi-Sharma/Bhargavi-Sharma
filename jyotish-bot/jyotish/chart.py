"""Builds the natal chart: positions, houses, nakshatras, vargas, dignities, aspects and states."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from . import ephemeris as eph
from .constants import (NAK_SPAN, NAKSHATRAS, PADA_SPAN, PLANETS, SIGN_LORD, SIGNS,
                        SPECIAL_ASPECTS, deg_in_sign, fmt_dms, house_from, sign_of)
from .dignity import baladi_avastha, dignity, jagradadi_avastha
from .variants import merged
from .vargas import ALL_VARGAS, varga_sign


@dataclass
class BirthData:
    name: str
    dt_local: datetime     # naive local date-time of birth
    tz: str | float        # IANA zone ("Asia/Kolkata") or UTC offset in hours
    lat: float
    lon: float
    place: str = ""
    gender: str = ""       # "M"/"F"/"" - some rules (spouse karaka) depend on it


def nakshatra_of(lon: float) -> dict:
    idx = int(lon // NAK_SPAN) % 27
    pada = int((lon % NAK_SPAN) // PADA_SPAN) + 1
    name, lord, deity, gana = NAKSHATRAS[idx]
    return {"index": idx, "name": name, "pada": pada, "lord": lord, "deity": deity, "gana": gana,
            "fraction_elapsed": (lon % NAK_SPAN) / NAK_SPAN}


def aspected_houses(p: str) -> list[int]:
    """Houses aspected, counted from the planet's own house (1 = itself)."""
    if p in SPECIAL_ASPECTS:
        return SPECIAL_ASPECTS[p]
    return [7]


NODE_SECONDARY_ASPECTS = [5, 9]


class Chart:
    def __init__(self, birth: BirthData, settings: dict | None = None):
        self.birth = birth
        self.settings = merged(settings)
        self.utc = eph.to_utc(birth.dt_local, birth.tz)
        self.jd = eph.julday(self.utc)
        self.snap = eph.snapshot(self.jd, self.settings, birth.lat, birth.lon)
        self.sun = eph.sun_events(self.jd, birth.lat, birth.lon)
        self.asc = self.snap.asc
        self.lagna = sign_of(self.asc)
        self.lon = {p: self.snap.bodies[p].lon for p in PLANETS}
        self.sign = {p: sign_of(self.lon[p]) for p in PLANETS}
        self.house = {p: house_from(self.lagna, self.sign[p]) for p in PLANETS}
        self.moon_sign = self.sign["Moon"]
        self.d1_signs = dict(self.sign)
        self.vargas = {d: {p: varga_sign(self.lon[p], d) for p in PLANETS} | {"Lagna": varga_sign(self.asc, d)}
                       for d in ALL_VARGAS}
        self.dig = {p: dignity(p, self.sign[p], deg_in_sign(self.lon[p]), self.d1_signs) for p in PLANETS}

    # ---- basic lookups -------------------------------------------------
    def lord_of_house(self, h: int, from_sign: int | None = None) -> str:
        base = self.lagna if from_sign is None else from_sign
        return SIGN_LORD[(base + h - 1) % 12]

    def houses_owned(self, p: str, from_sign: int | None = None) -> list[int]:
        base = self.lagna if from_sign is None else from_sign
        return [h for h in range(1, 13) if SIGN_LORD[(base + h - 1) % 12] == p]

    def occupants(self, h: int) -> list[str]:
        return [p for p in PLANETS if self.house[p] == h]

    def speed(self, p: str) -> float:
        return self.snap.bodies[p].speed

    def retro(self, p: str) -> bool:
        if p in ("Rahu", "Ketu"):
            return True  # nodes are always treated as retrograde
        return self.snap.bodies[p].speed < 0

    def aspects_of(self, p: str) -> list[dict]:
        """Planets and houses that planet p aspects (sign-based graha drishti)."""
        out = []
        for n in aspected_houses(p):
            target_house = (self.house[p] + n - 2) % 12 + 1
            out.append({"aspect": n, "house": target_house, "planets": self.occupants(target_house),
                        "primary": True})
        if p in ("Rahu", "Ketu"):
            for n in NODE_SECONDARY_ASPECTS:
                target_house = (self.house[p] + n - 2) % 12 + 1
                out.append({"aspect": n, "house": target_house, "planets": self.occupants(target_house),
                            "primary": False, "note": "disputed node aspect (see variants.node_aspects)"})
        return out

    def aspected_by(self, h: int, primary_only: bool = False) -> list[str]:
        res = []
        for p in PLANETS:
            for a in self.aspects_of(p):
                if a["house"] == h and (a["primary"] or not primary_only):
                    res.append(p if a["primary"] else f"{p} (secondary)")
        return res

    def planet_aspected_by(self, q: str, primary_only: bool = True) -> list[str]:
        nodes = ("Rahu", "Ketu")
        return [a for a in (x.split(" ")[0] for x in self.aspected_by(self.house[q], primary_only))
                if a != q and not (a in nodes and q in nodes)]

    def conjunct(self, p: str) -> list[str]:
        return [q for q in PLANETS if q != p and self.sign[q] == self.sign[p]]

    def connected(self, p: str, q: str) -> list[str]:
        """Ways two planets are related: conjunction, aspect either way, exchange, kendra."""
        ways = []
        if self.sign[p] == self.sign[q]:
            ways.append("conjunction")
        if q in self.planet_aspected_by(p):
            ways.append(f"{q} aspects {p}")
        if p in self.planet_aspected_by(q):
            ways.append(f"{p} aspects {q}")
        if SIGN_LORD[self.sign[p]] == q and SIGN_LORD[self.sign[q]] == p:
            ways.append("parivartana (sign exchange)")
        return ways

    # ---- per-planet record ---------------------------------------------
    def planet_row(self, p: str) -> dict:
        b = self.snap.bodies[p]
        nak = nakshatra_of(b.lon)
        deg = deg_in_sign(b.lon)
        return {
            "planet": p, "longitude": round(b.lon, 4), "sign": SIGNS[self.sign[p]],
            "degree": fmt_dms(deg), "degree_decimal": round(deg, 3),
            "house": self.house[p], "house_from_moon": house_from(self.moon_sign, self.sign[p]),
            "nakshatra": nak["name"], "pada": nak["pada"], "nakshatra_lord": nak["lord"],
            "sign_lord": SIGN_LORD[self.sign[p]], "retrograde": self.retro(p),
            "speed_deg_per_day": round(b.speed, 4), "dignity": self.dig[p],
            "navamsa": SIGNS[self.vargas[9][p]], "vargottama": self.vargas[9][p] == self.sign[p],
            "owns_houses": self.houses_owned(p),
            "baladi_avastha": baladi_avastha(self.sign[p], deg),
            "jagradadi_avastha": jagradadi_avastha(self.dig[p]),
            "conjunct": self.conjunct(p),
            "aspected_by": self.planet_aspected_by(p),
        }

    def lagna_row(self) -> dict:
        nak = nakshatra_of(self.asc)
        return {"sign": SIGNS[self.lagna], "degree": fmt_dms(deg_in_sign(self.asc)),
                "longitude": round(self.asc, 4), "lord": SIGN_LORD[self.lagna],
                "nakshatra": nak["name"], "pada": nak["pada"], "nakshatra_lord": nak["lord"],
                "navamsa": SIGNS[self.vargas[9]["Lagna"]]}

    def house_rows(self) -> list[dict]:
        rows = []
        for h in range(1, 13):
            s = (self.lagna + h - 1) % 12
            lord = SIGN_LORD[s]
            rows.append({"house": h, "sign": SIGNS[s], "lord": lord, "lord_in_house": self.house[lord],
                         "lord_dignity": self.dig[lord], "occupants": self.occupants(h),
                         "aspected_by": self.aspected_by(h)})
        return rows

    def bhava_chalit(self) -> list[dict]:
        """Equal houses with the ascendant degree as the bhava madhya (Sripati-style cusps at +/-15°).
        Planets whose chalit house differs from the whole-sign house are flagged."""
        shifts = []
        for p in PLANETS:
            rel = (self.lon[p] - self.asc + 15) % 360
            ch = int(rel // 30) + 1
            if ch != self.house[p]:
                shifts.append({"planet": p, "whole_sign_house": self.house[p], "chalit_house": ch})
        return shifts
