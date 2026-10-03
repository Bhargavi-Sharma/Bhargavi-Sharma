"""Registry of points where the classical texts (or their editions) disagree.

The engine never silently picks one side. For each disputed point it uses the
`default` below, states that in the report, and lists the alternatives so a
reading can say "per BPHS X, but per Phaladeepika Y".
"""

VARIANTS = {
    "ayanamsa": {
        "default": "lahiri",
        "options": ["lahiri", "raman", "krishnamurti", "yukteshwar", "true_chitra"],
        "note": "Lahiri (Chitrapaksha) is the Govt. of India standard (Calendar Reform Committee, 1955). "
                "The classical texts give no modern ayanamsa value; Raman ayanamsa differs by ~1.5°, "
                "enough to change the lagna, nakshatra pada and dasha balance for some charts.",
    },
    "node_type": {
        "default": "mean",
        "options": ["mean", "true"],
        "note": "Classical siddhantas compute the mean node. Many modern programs use the true node; "
                "the difference is up to ~1.5° and can shift Rahu/Ketu's nakshatra pada.",
    },
    "node_aspects": {
        "default": "7 only as primary; 5 and 9 listed as secondary",
        "note": "BPHS ch.26 gives special aspects only for Mars, Jupiter and Saturn. Some editions and later "
                "authors add 5th/9th (and sometimes 2nd/12th) aspects for Rahu/Ketu. They are reported "
                "separately and weighted lower.",
    },
    "node_exaltation": {
        "default": "Rahu exalted in Taurus, Ketu in Scorpio",
        "options": ["Taurus/Scorpio", "Gemini/Sagittarius"],
        "note": "BPHS ch.47 (Santhanam ed.) favours Taurus/Scorpio; several later works and the Jataka Parijata "
                "tradition use Gemini/Sagittarius. Node dignity is reported as tentative either way.",
    },
    "node_own_sign": {
        "default": "Rahu: Aquarius (co-lord), Ketu: Scorpio (co-lord)",
        "note": "Rahu is given Virgo as own sign in some BPHS editions and Aquarius as co-lordship in others.",
    },
    "combustion_orbs": {
        "default": {"Moon": 12, "Mars": 17, "Mercury": 14, "Mercury_retro": 12, "Jupiter": 11,
                    "Venus": 10, "Venus_retro": 8, "Saturn": 15},
        "note": "From Surya Siddhanta (ch.9). Some practitioners use a flat 8-10° for all planets; "
                "Phaladeepika treats combust planets as losing strength but notes the Moon's case separately.",
    },
    "dasha_year": {
        "default": 365.25,
        "options": [365.25, 365.2422, 360],
        "note": "BPHS is read by some as a 360-day savana year. 365.25 (Julian) is the common modern choice. "
                "Over a full 120-year cycle the choice moves dates by months, so near-boundary timings are marked.",
    },
    "chara_karaka_count": {
        "default": 7,
        "options": [7, 8],
        "note": "Jaimini Sutras use 7 karakas (Sun..Saturn). BPHS ch.32 also describes an 8-karaka scheme with "
                "Rahu (counted backwards from 30°). Both are shown when they differ.",
    },
    "planetary_war_winner": {
        "default": "planet with greater northern latitude wins",
        "note": "Surya Siddhanta ch.7: the planet north (higher latitude) is the winner. Other authors "
                "(e.g. some readings of Varahamihira) let the brighter planet win, so Venus usually wins. "
                "Both outcomes are reported when they differ.",
    },
    "hora_varga": {
        "default": "parashara",
        "note": "BPHS Parashari hora (only Leo/Cancer). Kashinatha and other horas give a 12-sign D2.",
    },
    "kaal_sarp": {
        "default": "reported as a modern combination",
        "note": "Kaal Sarp Yoga is not described in BPHS, Brihat Jataka, Saravali or Phaladeepika. It came from "
                "later popular texts. It is reported for completeness with that caveat and never used "
                "on its own to predict an event.",
    },
    "mangal_dosha_reference": {
        "default": "houses 1, 2, 4, 7, 8, 12 from Lagna, Moon and Venus",
        "note": "Some traditions omit the 1st house; some (South India) count from Lagna, Moon and Venus, "
                "others only from Lagna. Cancellation lists also differ across texts like Muhurta Martanda.",
    },
    "moolatrikona_moon": {
        "default": "Taurus 3°-30°",
        "note": "BPHS gives Taurus 4°-30° in some editions (3°-30° in others). Effect is small.",
    },
}


def merged(user: dict | None) -> dict:
    """Return the active settings: defaults overridden by any user choices."""
    out = {k: v.get("default") for k, v in VARIANTS.items()}
    if user:
        out.update({k: v for k, v in user.items() if k in VARIANTS})
    return out
