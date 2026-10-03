"""Descriptive profiles the classical texts allow: spouse's appearance and nature, children
(number, order, gender tendencies, pregnancy-loss indicators), career type, and mind.

These collect the indicators the texts use; the chat layer weighs them. Each indicator states
its basis so the reasoning can be audited."""
from __future__ import annotations

from .constants import PLANETS, SIGN_LORD, SIGNS, house_from
from .chart import nakshatra_of

# BPHS ch.3 (graha svarupa), abridged
PLANET_LOOKS = {
    "Sun": "square/medium build, honey-coloured eyes, little hair, dark-red/copper complexion, commanding",
    "Moon": "round face/body, fair complexion, soft and attractive eyes, gentle speech, changeable",
    "Mars": "youthful, medium-tall, thin waist, reddish complexion, sharp eyes; marks/scars or cuts",
    "Mercury": "slim, well-proportioned, greenish/wheatish (durva-grass) tone, witty, youthful-looking",
    "Jupiter": "large or heavy body, yellowish/golden tone, good eyes and hair, dignified",
    "Venus": "attractive, large beautiful eyes, curly/dark hair, mixed (variegated) complexion, charming",
    "Saturn": "lean and tall, dark complexion, coarse hair, prominent teeth/joints, looks older",
    "Rahu": "smoky/dark tone, tall, unconventional looks, possibly foreign/different background",
    "Ketu": "thin, rough skin, marks/scars, unusual or intense features",
}
# Sign build (Saravali / Brihat Jataka descriptions of the rising sign, abridged)
SIGN_LOOKS = {
    0: "medium height, lean, round eyes, mark on head likely", 1: "well-built, broad face/thighs, attractive",
    2: "tall-ish, long arms, expressive eyes", 3: "medium/short, plump, quick gait",
    4: "broad face and chest, large build, tawny eyes", 5: "slim, graceful, modest, youthful face",
    6: "tall, well-proportioned, prominent nose", 7: "medium, broad eyes and chest, strong body",
    8: "long face and neck, well-built", 9: "slender, weak lower limbs, deep eyes", 10: "tall, lean, prominent veins",
    11: "medium, well-proportioned, fish-like eyes, fair",
}
MARK_PLANETS = ("Mars", "Saturn", "Ketu", "Rahu")
# Kalapurusha: house/sign -> body region (BPHS ch.4 / Brihat Jataka 1.4)
BODY = {1: "head/forehead", 2: "face", 3: "neck/arms", 4: "chest", 5: "stomach", 6: "waist/abdomen",
        7: "lower abdomen", 8: "private parts", 9: "thighs", 10: "knees", 11: "calves", 12: "feet"}


def spouse(chart) -> dict:
    h7 = (chart.lagna + 6) % 12
    lord = SIGN_LORD[h7]
    occ = chart.occupants(7)
    asp = [p for p in chart.aspected_by(7, primary_only=True) if p not in occ]
    karaka = "Jupiter" if chart.birth.gender == "F" else "Venus"
    d9l = chart.vargas[9]["Lagna"]
    d9_7 = (d9l + 6) % 12
    d9_occ = [p for p in PLANETS if chart.vargas[9][p] == d9_7]
    indicators = [
        {"factor": f"7th sign {SIGNS[h7]}", "suggests": SIGN_LOOKS[h7], "weight": "high"},
        {"factor": f"7th lord {lord} in {SIGNS[chart.sign[lord]]} (house {chart.house[lord]})",
         "suggests": PLANET_LOOKS[lord], "weight": "high"},
    ]
    for p in occ:
        indicators.append({"factor": f"{p} in 7th", "suggests": PLANET_LOOKS[p], "weight": "highest"})
    for p in asp:
        indicators.append({"factor": f"{p} aspects 7th", "suggests": PLANET_LOOKS[p], "weight": "medium"})
    indicators.append({"factor": f"D9 7th sign {SIGNS[d9_7]}", "suggests": SIGN_LOOKS[d9_7], "weight": "high"})
    for p in d9_occ:
        indicators.append({"factor": f"{p} in D9 7th", "suggests": PLANET_LOOKS[p], "weight": "high"})
    indicators.append({"factor": f"karaka {karaka} in {SIGNS[chart.sign[karaka]]}",
                       "suggests": PLANET_LOOKS[karaka], "weight": "medium"})
    marks = []
    for p in MARK_PLANETS:
        if p in occ or p in asp:
            marks.append(f"{p} influences the 7th: a mark/scar/injury is indicated on the spouse; body region by the "
                         f"sign it occupies counted from the 7th (Kalapurusha) - {p} is in sign "
                         f"{SIGNS[chart.sign[p]]}, {house_from(h7, chart.sign[p])} from the 7th = "
                         f"{BODY[house_from(h7, chart.sign[p])]}")
    lh = chart.house[lord]
    direction = next(k for k, v in {"near (kendra)": [1, 4, 7, 10], "moderate distance": [2, 5, 8, 11],
                                    "far / possibly foreign": [3, 6, 9, 12]}.items() if lh in v)
    return {"indicators": indicators, "marks": marks,
            "distance_of_spouse_origin": f"7th lord in house {lh}: {direction} (popular rule)",
            "darakaraka_note": "See jaimini.chara_karakas for Darakaraka; its sign/nakshatra add to the description",
            "method": "Describe by combining: planets IN the 7th (strongest) > 7th lord > D9 7th > aspects > karaka. "
                      "Where indicators conflict, say so."}


MALE_SIGNS = (0, 2, 4, 6, 8, 10)


def children(chart) -> dict:
    h5 = (chart.lagna + 4) % 12
    lord = SIGN_LORD[h5]
    occ = chart.occupants(5)
    d7l = chart.vargas[7]["Lagna"]
    d7_5 = (d7l + 4) % 12
    ind = []
    loss = []
    for p in occ:
        if p in ("Mars", "Saturn", "Rahu", "Ketu"):
            loss.append(f"{p} in 5th (BPHS progeny chapter: malefic in 5th troubles progeny; Rahu/Ketu/Mars may "
                        "indicate loss of pregnancy or surgery-related birth)")
    if chart.house[lord] in (6, 8, 12):
        loss.append(f"5th lord {lord} in dusthana {chart.house[lord]} - delays/obstacles to progeny")
    if chart.dig[lord] == "Debilitated":
        loss.append(f"5th lord {lord} debilitated")
    j = chart.dig["Jupiter"]
    if j in ("Debilitated", "Enemy", "Great Enemy") or chart.house["Jupiter"] in (6, 8, 12):
        loss.append(f"putrakaraka Jupiter weak ({j}, house {chart.house['Jupiter']})")
    mal_asp = [p for p in chart.aspected_by(5, primary_only=True) if p in ("Mars", "Saturn")]
    if mal_asp:
        loss.append(f"5th aspected by {mal_asp}")
    sex = []
    for p in occ + [lord]:
        g = "male" if p in ("Sun", "Mars", "Jupiter") else "female" if p in ("Moon", "Venus") else "neuter (follows sign)"
        sex.append(f"{p}: {g}")
    sex.append(f"5th sign {SIGNS[h5]}: {'male' if h5 in MALE_SIGNS else 'female'}")
    sex.append(f"D7 5th sign {SIGNS[d7_5]}: {'male' if d7_5 in MALE_SIGNS else 'female'}")
    navamshas_crossed = int((chart.lon[lord] % 30) // (30 / 9)) + 1
    ind.append(f"5th lord {lord} has crossed {navamshas_crossed} navamsha(s) in its sign - an old rule gives the "
               "count of children by navamshas (Phaladeepika ch.12); treat as a rough indicator only")
    return {"fifth_house": SIGNS[h5], "fifth_lord": lord, "occupants": occ, "d7_lagna": SIGNS[d7l],
            "d7_fifth": SIGNS[d7_5], "d7_fifth_occupants": [p for p in PLANETS if chart.vargas[7][p] == d7_5],
            "gender_indicators": sex, "pregnancy_obstacle_indicators": loss, "count_indicators": ind,
            "method": "Order of children: 5th house = 1st child, 7th = 2nd, 9th = 3rd (each 3rd from previous) - "
                      "judge each with its lord; time each with dasha of those significators + Jupiter transit."}


def career(chart) -> dict:
    l10 = chart.lord_of_house(10)
    occ = chart.occupants(10)
    d10l = chart.vargas[10]["Lagna"]
    d10_10 = (d10l + 9) % 12
    fields = {
        "Sun": "government, administration, politics, medicine, authority roles",
        "Moon": "public dealing, hospitality, nursing, food, liquids, travel, psychology",
        "Mars": "army/police, engineering, surgery, real estate, sports, machinery",
        "Mercury": "commerce, accounts, IT, writing, media, teaching, analysis",
        "Jupiter": "teaching, law, finance/banking, advisory, religion, management",
        "Venus": "arts, fashion, beauty, entertainment, luxury goods, hospitality, vehicles",
        "Saturn": "labour-intensive industry, mining, oil, service/large organisations, judiciary, construction",
        "Rahu": "technology, foreign companies, aviation, unconventional/new fields, research",
        "Ketu": "research, spirituality, coding/occult, isolated technical work",
    }
    disp_navamsa_lord = SIGN_LORD[chart.vargas[9][l10]]
    govt = []
    if chart.house["Sun"] in (1, 10, 11, 9) and chart.dig["Sun"] not in ("Debilitated",):
        govt.append(f"Sun in house {chart.house['Sun']}")
    if "Sun" in occ or l10 == "Sun":
        govt.append("Sun linked to 10th")
    if chart.house["Moon"] == 10:
        govt.append("Moon in 10th")
    return {"tenth_sign": SIGNS[(chart.lagna + 9) % 12], "tenth_lord": l10, "occupants": occ,
            "field_indicators": {p: fields[p] for p in dict.fromkeys(occ + [l10, disp_navamsa_lord])},
            "d10_tenth": SIGNS[d10_10], "d10_tenth_occupants": [p for p in PLANETS if chart.vargas[10][p] == d10_10],
            "navamsa_dispositor_of_10th_lord": disp_navamsa_lord,
            "govt_job_indicators": govt,
            "self_employed_vs_service": ("business tendency (7th/3rd strong, Mercury/Venus to 10th)"
                                         if chart.house[l10] in (3, 7, 11) else
                                         "service tendency (6th/10th/Saturn link)" if chart.house[l10] in (6, 10)
                                         else "mixed - judge with D10"),
            "method": "Profession by: planets in 10th, 10th lord, navamsa dispositor of 10th lord (Phaladeepika ch.5), "
                      "D10, Amatyakaraka."}


def mind(chart) -> dict:
    m = []
    moon_conj = chart.conjunct("Moon")
    for p in ("Saturn", "Rahu", "Ketu", "Mars"):
        if p in moon_conj:
            m.append(f"Moon with {p}")
        if p in chart.planet_aspected_by("Moon"):
            m.append(f"{p} aspects Moon")
    if chart.dig["Moon"] in ("Debilitated", "Enemy", "Great Enemy"):
        m.append(f"Moon {chart.dig['Moon']}")
    if chart.house["Moon"] in (6, 8, 12):
        m.append(f"Moon in dusthana {chart.house['Moon']}")
    el = (chart.lon["Moon"] - chart.lon["Sun"]) % 360
    if el < 72 or el > 288:
        m.append("dark (weak) Moon near amavasya")
    if chart.dig["Mercury"] == "Debilitated" or "Rahu" in chart.conjunct("Mercury"):
        m.append("Mercury afflicted (overthinking/nervous stress)")
    good = []
    if "Jupiter" in chart.planet_aspected_by("Moon") or "Jupiter" in moon_conj:
        good.append("Jupiter protects the Moon")
    if chart.dig["Moon"] in ("Exalted", "Own", "Moolatrikona"):
        good.append(f"Moon {chart.dig['Moon']}")
    if chart.house["Moon"] in (1, 4, 7, 10, 5, 9):
        good.append(f"Moon in good house {chart.house['Moon']}")
    return {"stressors": m, "stabilisers": good, "moon_nakshatra": nakshatra_of(chart.lon["Moon"])["name"],
            "fourth_lord": chart.lord_of_house(4), "fourth_lord_house": chart.house[chart.lord_of_house(4)]}


def all_profiles(chart) -> dict:
    return {"spouse": spouse(chart), "children": children(chart), "career": career(chart), "mind": mind(chart)}
