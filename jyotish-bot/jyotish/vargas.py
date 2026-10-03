"""Divisional charts (BPHS ch.6-7). Each function maps a sidereal longitude to a sign index."""
from .constants import MODALITY, is_odd

VARGA_NAMES = {
    1: "Rashi (D1) - body, overall life", 2: "Hora (D2) - wealth", 3: "Drekkana (D3) - siblings, courage",
    4: "Chaturthamsha (D4) - property, fortune", 7: "Saptamsha (D7) - children",
    9: "Navamsha (D9) - spouse, dharma, inner strength of planets", 10: "Dashamsha (D10) - career",
    12: "Dwadashamsha (D12) - parents", 16: "Shodashamsha (D16) - vehicles, comforts",
    20: "Vimshamsha (D20) - spiritual practice", 24: "Chaturvimshamsha (D24) - education",
    27: "Saptavimshamsha (D27) - strengths/weaknesses", 30: "Trimshamsha (D30) - misfortunes, character",
    40: "Khavedamsha (D40) - maternal legacy", 45: "Akshavedamsha (D45) - paternal legacy, conduct",
    60: "Shashtiamsha (D60) - past karma (needs exact birth time)",
}


def _part(lon: float, n: int) -> tuple[int, int]:
    sign = int(lon // 30) % 12
    part = int((lon % 30) / (30 / n))
    return sign, min(part, n - 1)


def varga_sign(lon: float, d: int) -> int:
    lon %= 360
    s, p = _part(lon, d) if d != 1 else (int(lon // 30), 0)
    mod = MODALITY[s]
    if d == 1:
        return s
    if d == 2:  # Parashari hora: odd sign 0-15 Sun(Leo), 15-30 Moon(Cancer); even sign reversed
        first_half = p == 0
        return (4 if first_half else 3) if is_odd(s) else (3 if first_half else 4)
    if d == 3:
        return (s + 4 * p) % 12
    if d == 4:
        return (s + 3 * p) % 12
    if d == 7:
        return (s + p) % 12 if is_odd(s) else (s + 6 + p) % 12
    if d == 9:
        return int(lon / (30 / 9)) % 12
    if d == 10:
        return (s + p) % 12 if is_odd(s) else (s + 8 + p) % 12
    if d == 12:
        return (s + p) % 12
    if d == 16:
        start = {"Movable": 0, "Fixed": 4, "Dual": 8}[mod]
        return (start + p) % 12
    if d == 20:
        start = {"Movable": 0, "Fixed": 8, "Dual": 4}[mod]
        return (start + p) % 12
    if d == 24:
        return ((4 if is_odd(s) else 3) + p) % 12
    if d == 27:
        return int(lon / (30 / 27)) % 12
    if d == 30:
        deg = lon % 30
        if is_odd(s):  # Mars, Saturn, Jupiter, Mercury, Venus
            for lim, sign in ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)):
                if deg < lim:
                    return sign
        else:          # Venus, Mercury, Jupiter, Saturn, Mars
            for lim, sign in ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7)):
                if deg < lim:
                    return sign
        return s
    if d == 40:
        return ((0 if is_odd(s) else 6) + p) % 12
    if d == 45:
        start = {"Movable": 0, "Fixed": 4, "Dual": 8}[mod]
        return (start + p) % 12
    if d == 60:
        return (s + p) % 12
    raise ValueError(f"unsupported varga D{d}")


ALL_VARGAS = sorted(VARGA_NAMES)
