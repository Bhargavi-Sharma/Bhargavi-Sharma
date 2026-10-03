"""Fixed classical tables. Sources are cited inline; disputed values live in variants.py."""

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN = PLANETS[:7]  # the seven visible grahas used in shadbala / ashtakavarga

HINDI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "गुरु",
    "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
}

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_SA = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]

# BPHS ch.3/4 - sign lords
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
             "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

ELEMENT = ["Fire", "Earth", "Air", "Water"] * 3
MODALITY = ["Movable", "Fixed", "Dual"] * 4  # chara / sthira / dvisvabhava


def is_odd(sign: int) -> bool:
    """Odd (male) signs are Aries, Gemini, ... (index 0, 2, ...)."""
    return sign % 2 == 0


OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
    "Venus": [1, 6], "Saturn": [9, 10],
}

# BPHS ch.3 - deep exaltation (sign, degree). Debilitation is the opposite point.
EXALTATION = {
    "Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
    "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20),
}

# BPHS ch.3 - moolatrikona (sign, from_deg, to_deg)
MOOLATRIKONA = {
    "Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 15, 20),
    "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20),
}

# BPHS ch.3 - natural (naisargika) relationships
NATURAL_FRIENDS = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutral": ["Mercury"], "enemies": ["Venus", "Saturn"]},
    "Moon": {"friends": ["Sun", "Mercury"], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutral": ["Venus", "Saturn"], "enemies": ["Mercury"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutral": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutral": ["Saturn"], "enemies": ["Mercury", "Venus"]},
    "Venus": {"friends": ["Mercury", "Saturn"], "neutral": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "neutral": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
}

NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]  # Moon when waxing, Mercury when unafflicted
NATURAL_MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

# BPHS ch.3 - karakatva (significations), abridged
KARAKA = {
    "Sun": "soul, father, authority, government, health/vitality, bones, heart, right eye (male)",
    "Moon": "mind, mother, emotions, fluids, public, left eye (male), nourishment",
    "Mars": "siblings (younger), courage, land/property, police/army, blood, surgery, accidents",
    "Mercury": "intellect, speech, business, communication, maternal uncle, skin, nervous system",
    "Jupiter": "children, guru, wisdom, dharma, wealth, husband (in a woman's chart), liver",
    "Venus": "spouse/wife (in a man's chart), love, luxury, vehicles, arts, semen, kidneys",
    "Saturn": "longevity, sorrow, labour, servants, delays, discipline, legs, chronic disease",
    "Rahu": "foreign things, obsession, sudden events, maternal grandfather, technology, poison",
    "Ketu": "moksha, detachment, spirituality, paternal grandfather, sudden loss, wounds",
}

# Chara-karaka-independent house karakas (BPHS ch.32)
BHAVA_KARAKA = {
    1: ["Sun"], 2: ["Jupiter"], 3: ["Mars"], 4: ["Moon", "Mercury"], 5: ["Jupiter"],
    6: ["Mars", "Saturn"], 7: ["Venus"], 8: ["Saturn"], 9: ["Sun", "Jupiter"],
    10: ["Sun", "Mercury", "Jupiter", "Saturn"], 11: ["Jupiter"], 12: ["Saturn"],
}

BHAVA_MEANING = {
    1: "Tanu - self, body, health, personality, overall life direction",
    2: "Dhana - wealth, family, speech, food, early education, face, right eye",
    3: "Sahaja - younger siblings, courage, effort, short travel, communication, hands",
    4: "Sukha - mother, home, property, vehicles, happiness, schooling, heart",
    5: "Putra - children, intelligence, past merit (purva punya), romance, mantra, speculation",
    6: "Ripu - enemies, disease, debts, litigation, service, competition, maternal uncle",
    7: "Kalatra - spouse, marriage, partnership, business, public dealings, travel abroad",
    8: "Ayu - longevity, sudden events, inheritance, hidden matters, research, chronic illness",
    9: "Dharma - father, guru, fortune (bhagya), higher learning, long journeys, religion",
    10: "Karma - career, status, actions, authority, fame",
    11: "Labha - gains, income, elder siblings, friends, fulfilment of desires",
    12: "Vyaya - losses, expenses, foreign residence, bed pleasures, moksha, hospital/isolation",
}

KENDRA = [1, 4, 7, 10]
TRIKONA = [1, 5, 9]
DUSTHANA = [6, 8, 12]
UPACHAYA = [3, 6, 10, 11]
PANAPHARA = [2, 5, 8, 11]
APOKLIMA = [3, 6, 9, 12]

# Nakshatras: (name, lord, deity, gana)
NAKSHATRAS = [
    ("Ashwini", "Ketu", "Ashwini Kumaras", "Deva"),
    ("Bharani", "Venus", "Yama", "Manushya"),
    ("Krittika", "Sun", "Agni", "Rakshasa"),
    ("Rohini", "Moon", "Prajapati", "Manushya"),
    ("Mrigashira", "Mars", "Soma", "Deva"),
    ("Ardra", "Rahu", "Rudra", "Manushya"),
    ("Punarvasu", "Jupiter", "Aditi", "Deva"),
    ("Pushya", "Saturn", "Brihaspati", "Deva"),
    ("Ashlesha", "Mercury", "Nagas", "Rakshasa"),
    ("Magha", "Ketu", "Pitris", "Rakshasa"),
    ("Purva Phalguni", "Venus", "Bhaga", "Manushya"),
    ("Uttara Phalguni", "Sun", "Aryaman", "Manushya"),
    ("Hasta", "Moon", "Savitr", "Deva"),
    ("Chitra", "Mars", "Tvashtr", "Rakshasa"),
    ("Swati", "Rahu", "Vayu", "Deva"),
    ("Vishakha", "Jupiter", "Indra-Agni", "Rakshasa"),
    ("Anuradha", "Saturn", "Mitra", "Deva"),
    ("Jyeshtha", "Mercury", "Indra", "Rakshasa"),
    ("Mula", "Ketu", "Nirriti", "Rakshasa"),
    ("Purva Ashadha", "Venus", "Apas", "Manushya"),
    ("Uttara Ashadha", "Sun", "Vishvedevas", "Manushya"),
    ("Shravana", "Moon", "Vishnu", "Deva"),
    ("Dhanishta", "Mars", "Vasus", "Rakshasa"),
    ("Shatabhisha", "Rahu", "Varuna", "Rakshasa"),
    ("Purva Bhadrapada", "Jupiter", "Aja Ekapada", "Manushya"),
    ("Uttara Bhadrapada", "Saturn", "Ahir Budhnya", "Manushya"),
    ("Revati", "Mercury", "Pushan", "Deva"),
]
NAK_SPAN = 360.0 / 27  # 13°20'
PADA_SPAN = NAK_SPAN / 4  # 3°20'

# Gandanta / Gandmool nakshatras (junctions of water and fire signs)
GANDMOOL = ["Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"]

# Vimshottari (BPHS ch.46)
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# Graha drishti (BPHS ch.26) - houses counted from the planet, inclusive
SPECIAL_ASPECTS = {"Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10]}

# Dig bala: house in which each planet gets full directional strength (BPHS ch.27)
DIG_BALA_HOUSE = {"Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1,
                  "Moon": 4, "Venus": 4, "Saturn": 7}

# Naisargika bala in virupas (BPHS ch.27)
NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}

# Required shadbala in rupas (BPHS ch.27)
SHADBALA_REQUIRED = {"Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
                     "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}

# Weekday lords, Sunday = 0
WEEKDAY_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
# Chaldean hora order
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

GENDER = {"Sun": "M", "Mars": "M", "Jupiter": "M", "Moon": "F", "Venus": "F",
          "Mercury": "N", "Saturn": "N", "Rahu": "N", "Ketu": "N"}

# Mean daily motion (deg/day), used to classify chesta (motion) states
MEAN_SPEED = {"Sun": 0.9856, "Moon": 13.176, "Mars": 0.524, "Mercury": 1.383,
              "Jupiter": 0.083, "Venus": 1.2, "Saturn": 0.0335}


def sign_of(lon: float) -> int:
    return int(lon // 30) % 12


def deg_in_sign(lon: float) -> float:
    return lon % 30


def house_from(sign_from: int, sign_to: int) -> int:
    """1-based house number of sign_to counted from sign_from."""
    return (sign_to - sign_from) % 12 + 1


def fmt_dms(deg: float) -> str:
    d = int(deg)
    m_f = (deg - d) * 60
    m = int(m_f)
    s = int(round((m_f - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d}°{m:02d}'{s:02d}\""
