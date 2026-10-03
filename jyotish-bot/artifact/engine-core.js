/* Jyotish engine (JavaScript port of jyotish-bot/jyotish/*.py): constants, chart, vargas, dignity,
   functional nature, dasha, ashtakavarga, shadbala. Shared namespace: J. */
(function (root) {
  const Astro = root.Astro || require("./astro.js");
  const J = root.J || (root.J = {});
  J.Astro = Astro;

  // ---------------------------------------------------------------- constants
  const PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
  const SEVEN = PLANETS.slice(0, 7);
  const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
    "Capricorn", "Aquarius", "Pisces"];
  const SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Saturn", "Jupiter"];
  const MODALITY = Array.from({ length: 12 }, (_, i) => ["Movable", "Fixed", "Dual"][i % 3]);
  const isOdd = s => s % 2 === 0;
  const OWN_SIGNS = { Sun: [4], Moon: [3], Mars: [0, 7], Mercury: [2, 5], Jupiter: [8, 11], Venus: [1, 6], Saturn: [9, 10] };
  const EXALTATION = { Sun: [0, 10], Moon: [1, 3], Mars: [9, 28], Mercury: [5, 15], Jupiter: [3, 5], Venus: [11, 27], Saturn: [6, 20] };
  const MOOLATRIKONA = { Sun: [4, 0, 20], Moon: [1, 3, 30], Mars: [0, 0, 12], Mercury: [5, 15, 20], Jupiter: [8, 0, 10],
    Venus: [6, 0, 15], Saturn: [10, 0, 20] };
  const NATURAL_FRIENDS = {
    Sun: { friends: ["Moon", "Mars", "Jupiter"], neutral: ["Mercury"], enemies: ["Venus", "Saturn"] },
    Moon: { friends: ["Sun", "Mercury"], neutral: ["Mars", "Jupiter", "Venus", "Saturn"], enemies: [] },
    Mars: { friends: ["Sun", "Moon", "Jupiter"], neutral: ["Venus", "Saturn"], enemies: ["Mercury"] },
    Mercury: { friends: ["Sun", "Venus"], neutral: ["Mars", "Jupiter", "Saturn"], enemies: ["Moon"] },
    Jupiter: { friends: ["Sun", "Moon", "Mars"], neutral: ["Saturn"], enemies: ["Mercury", "Venus"] },
    Venus: { friends: ["Mercury", "Saturn"], neutral: ["Mars", "Jupiter"], enemies: ["Sun", "Moon"] },
    Saturn: { friends: ["Mercury", "Venus"], neutral: ["Jupiter"], enemies: ["Sun", "Moon", "Mars"] },
  };
  const NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"];
  const NAKSHATRAS = [
    ["Ashwini", "Ketu", "Ashwini Kumaras", "Deva"], ["Bharani", "Venus", "Yama", "Manushya"],
    ["Krittika", "Sun", "Agni", "Rakshasa"], ["Rohini", "Moon", "Prajapati", "Manushya"],
    ["Mrigashira", "Mars", "Soma", "Deva"], ["Ardra", "Rahu", "Rudra", "Manushya"],
    ["Punarvasu", "Jupiter", "Aditi", "Deva"], ["Pushya", "Saturn", "Brihaspati", "Deva"],
    ["Ashlesha", "Mercury", "Nagas", "Rakshasa"], ["Magha", "Ketu", "Pitris", "Rakshasa"],
    ["Purva Phalguni", "Venus", "Bhaga", "Manushya"], ["Uttara Phalguni", "Sun", "Aryaman", "Manushya"],
    ["Hasta", "Moon", "Savitr", "Deva"], ["Chitra", "Mars", "Tvashtr", "Rakshasa"],
    ["Swati", "Rahu", "Vayu", "Deva"], ["Vishakha", "Jupiter", "Indra-Agni", "Rakshasa"],
    ["Anuradha", "Saturn", "Mitra", "Deva"], ["Jyeshtha", "Mercury", "Indra", "Rakshasa"],
    ["Mula", "Ketu", "Nirriti", "Rakshasa"], ["Purva Ashadha", "Venus", "Apas", "Manushya"],
    ["Uttara Ashadha", "Sun", "Vishvedevas", "Manushya"], ["Shravana", "Moon", "Vishnu", "Deva"],
    ["Dhanishta", "Mars", "Vasus", "Rakshasa"], ["Shatabhisha", "Rahu", "Varuna", "Rakshasa"],
    ["Purva Bhadrapada", "Jupiter", "Aja Ekapada", "Manushya"], ["Uttara Bhadrapada", "Saturn", "Ahir Budhnya", "Manushya"],
    ["Revati", "Mercury", "Pushan", "Deva"],
  ];
  const NAK_SPAN = 360 / 27, PADA_SPAN = NAK_SPAN / 4;
  const GANDMOOL = ["Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"];
  const DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"];
  const DASHA_YEARS = { Ketu: 7, Venus: 20, Sun: 6, Moon: 10, Mars: 7, Rahu: 18, Jupiter: 16, Saturn: 19, Mercury: 17 };
  const SPECIAL_ASPECTS = { Mars: [4, 7, 8], Jupiter: [5, 7, 9], Saturn: [3, 7, 10] };
  const DIG_BALA_HOUSE = { Sun: 10, Mars: 10, Jupiter: 1, Mercury: 1, Moon: 4, Venus: 4, Saturn: 7 };
  const NAISARGIKA = { Sun: 60.0, Moon: 51.43, Venus: 42.86, Jupiter: 34.29, Mercury: 25.71, Mars: 17.14, Saturn: 8.57 };
  const SHADBALA_REQUIRED = { Sun: 6.5, Moon: 6.0, Mars: 5.0, Mercury: 7.0, Jupiter: 6.5, Venus: 5.5, Saturn: 5.0 };
  const WEEKDAY_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const GENDER = { Sun: "M", Mars: "M", Jupiter: "M", Moon: "F", Venus: "F", Mercury: "N", Saturn: "N", Rahu: "N", Ketu: "N" };
  const MEAN_SPEED = { Sun: 0.9856, Moon: 13.176, Mars: 0.524, Mercury: 1.383, Jupiter: 0.083, Venus: 1.2, Saturn: 0.0335 };
  const BHAVA_MEANING = {
    1: "Tanu - self, body, health, personality", 2: "Dhana - wealth, family, speech, food", 3: "Sahaja - siblings, courage, effort",
    4: "Sukha - mother, home, property, vehicles, happiness", 5: "Putra - children, intelligence, purva punya, romance",
    6: "Ripu - enemies, disease, debts, service", 7: "Kalatra - spouse, marriage, partnership",
    8: "Ayu - longevity, sudden events, inheritance, hidden matters", 9: "Dharma - father, guru, fortune, higher learning",
    10: "Karma - career, status, authority", 11: "Labha - gains, income, elder siblings, friends",
    12: "Vyaya - losses, expenses, foreign residence, moksha",
  };

  const signOf = lon => Math.floor(Astro.norm(lon) / 30) % 12;
  const degIn = lon => Astro.norm(lon) % 30;
  const houseFrom = (a, b) => (((b - a) % 12) + 12) % 12 + 1;
  const pyList = a => "[" + a.map(x => `'${x}'`).join(", ") + "]";
  const round = (x, n = 2) => {
    const f = 10 ** n, y = x * f, fl = Math.floor(y), diff = y - fl;
    const r = Math.abs(diff - 0.5) < 1e-9 ? (fl % 2 === 0 ? fl : fl + 1) : Math.round(y);
    return r / f;
  };
  const pyNum = x => (Number.isInteger(x) ? x.toFixed(1) : String(x));
  function fmtDms(deg) {
    let d = Math.floor(deg), mf = (deg - d) * 60, m = Math.floor(mf), s = Math.round((mf - m) * 60);
    if (s === 60) { s = 0; m += 1; }
    if (m === 60) { m = 0; d += 1; }
    return `${d}°${String(m).padStart(2, "0")}'${String(s).padStart(2, "0")}"`;
  }

  // ---------------------------------------------------------------- variants
  const VARIANTS = {
    ayanamsa: { default: "lahiri", note: "Lahiri (Chitrapaksha) is the Govt. of India standard (Calendar Reform Committee, 1955). The classical texts give no modern ayanamsa value; Raman ayanamsa differs by ~1.5°, enough to change the lagna, nakshatra pada and dasha balance for some charts." },
    node_type: { default: "mean", note: "Classical siddhantas compute the mean node. Many modern programs use the true node; the difference is up to ~1.5° and can shift Rahu/Ketu's nakshatra pada." },
    node_aspects: { default: "7 only as primary; 5 and 9 listed as secondary", note: "BPHS ch.26 gives special aspects only for Mars, Jupiter and Saturn. Some editions and later authors add 5th/9th (and sometimes 2nd/12th) aspects for Rahu/Ketu. They are reported separately and weighted lower." },
    node_exaltation: { default: "Rahu exalted in Taurus, Ketu in Scorpio", note: "BPHS ch.47 (Santhanam ed.) favours Taurus/Scorpio; several later works and the Jataka Parijata tradition use Gemini/Sagittarius. Node dignity is reported as tentative either way." },
    node_own_sign: { default: "Rahu: Aquarius (co-lord), Ketu: Scorpio (co-lord)", note: "Rahu is given Virgo as own sign in some BPHS editions and Aquarius as co-lordship in others." },
    combustion_orbs: { default: {"Moon": 12, "Mars": 17, "Mercury": 14, "Mercury_retro": 12, "Jupiter": 11, "Venus": 10, "Venus_retro": 8, "Saturn": 15}, note: "From Surya Siddhanta (ch.9). Some practitioners use a flat 8-10° for all planets; Phaladeepika treats combust planets as losing strength but notes the Moon's case separately." },
    dasha_year: { default: 365.25, note: "BPHS is read by some as a 360-day savana year. 365.25 (Julian) is the common modern choice. Over a full 120-year cycle the choice moves dates by months, so near-boundary timings are marked." },
    chara_karaka_count: { default: 7, note: "Jaimini Sutras use 7 karakas (Sun..Saturn). BPHS ch.32 also describes an 8-karaka scheme with Rahu (counted backwards from 30°). Both are shown when they differ." },
    planetary_war_winner: { default: "planet with greater northern latitude wins", note: "Surya Siddhanta ch.7: the planet north (higher latitude) is the winner. Other authors (e.g. some readings of Varahamihira) let the brighter planet win, so Venus usually wins. Both outcomes are reported when they differ." },
    hora_varga: { default: "parashara", note: "BPHS Parashari hora (only Leo/Cancer). Kashinatha and other horas give a 12-sign D2." },
    kaal_sarp: { default: "reported as a modern combination", note: "Kaal Sarp Yoga is not described in BPHS, Brihat Jataka, Saravali or Phaladeepika. It came from later popular texts. It is reported for completeness with that caveat and never used on its own to predict an event." },
    mangal_dosha_reference: { default: "houses 1, 2, 4, 7, 8, 12 from Lagna, Moon and Venus", note: "Some traditions omit the 1st house; some (South India) count from Lagna, Moon and Venus, others only from Lagna. Cancellation lists also differ across texts like Muhurta Martanda." },
    moolatrikona_moon: { default: "Taurus 3\u00b0-30\u00b0", note: "BPHS gives Taurus 4°-30° in some editions (3°-30° in others). Effect is small." },
  };
  const defaults = () => Object.fromEntries(Object.entries(VARIANTS).map(([k, v]) => [k, v.default]));

  // ---------------------------------------------------------------- vargas
  const VARGA_NAMES = {"1": "Rashi (D1) - body, overall life", "2": "Hora (D2) - wealth", "3": "Drekkana (D3) - siblings, courage", "4": "Chaturthamsha (D4) - property, fortune", "7": "Saptamsha (D7) - children", "9": "Navamsha (D9) - spouse, dharma, inner strength of planets", "10": "Dashamsha (D10) - career", "12": "Dwadashamsha (D12) - parents", "16": "Shodashamsha (D16) - vehicles, comforts", "20": "Vimshamsha (D20) - spiritual practice", "24": "Chaturvimshamsha (D24) - education", "27": "Saptavimshamsha (D27) - strengths/weaknesses", "30": "Trimshamsha (D30) - misfortunes, character", "40": "Khavedamsha (D40) - maternal legacy", "45": "Akshavedamsha (D45) - paternal legacy, conduct", "60": "Shashtiamsha (D60) - past karma (needs exact birth time)"};
  const ALL_VARGAS = Object.keys(VARGA_NAMES).map(Number).sort((a, b) => a - b);
  function vargaSign(lon, d) {
    lon = Astro.norm(lon);
    const s = Math.floor(lon / 30) % 12;
    const p = Math.min(Math.floor((lon % 30) / (30 / d)), d - 1);
    const mod = MODALITY[s];
    switch (d) {
      case 1: return s;
      case 2: return isOdd(s) ? (p === 0 ? 4 : 3) : (p === 0 ? 3 : 4);
      case 3: return (s + 4 * p) % 12;
      case 4: return (s + 3 * p) % 12;
      case 7: return isOdd(s) ? (s + p) % 12 : (s + 6 + p) % 12;
      case 9: return Math.floor(lon / (30 / 9)) % 12;
      case 10: return isOdd(s) ? (s + p) % 12 : (s + 8 + p) % 12;
      case 12: return (s + p) % 12;
      case 16: return ({ Movable: 0, Fixed: 4, Dual: 8 }[mod] + p) % 12;
      case 20: return ({ Movable: 0, Fixed: 8, Dual: 4 }[mod] + p) % 12;
      case 24: return ((isOdd(s) ? 4 : 3) + p) % 12;
      case 27: return Math.floor(lon / (30 / 27)) % 12;
      case 30: {
        const deg = lon % 30;
        const t = isOdd(s) ? [[5, 0], [10, 10], [18, 8], [25, 2], [30, 6]] : [[5, 1], [12, 5], [20, 11], [25, 9], [30, 7]];
        for (const [lim, sg] of t) if (deg < lim) return sg;
        return s;
      }
      case 40: return ((isOdd(s) ? 0 : 6) + p) % 12;
      case 45: return ({ Movable: 0, Fixed: 4, Dual: 8 }[mod] + p) % 12;
      case 60: return (s + p) % 12;
    }
    throw new Error("unsupported varga D" + d);
  }

  // ---------------------------------------------------------------- dignity
  const NODE_EXALT = { Rahu: 1, Ketu: 7 }, NODE_DEBIL = { Rahu: 7, Ketu: 1 }, NODE_OWN = { Rahu: [10], Ketu: [7] };
  const NODE_FRIENDS = { Rahu: ["Venus", "Saturn", "Mercury"], Ketu: ["Mars", "Venus", "Saturn"] };
  const NODE_ENEMIES = { Rahu: ["Sun", "Moon", "Mars"], Ketu: ["Sun", "Moon"] };
  function naturalRel(p, q) {
    if (NODE_FRIENDS[p]) return NODE_FRIENDS[p].includes(q) ? "F" : NODE_ENEMIES[p].includes(q) ? "E" : "N";
    if (q === "Rahu" || q === "Ketu") return "N";
    const t = NATURAL_FRIENDS[p];
    return t.friends.includes(q) ? "F" : t.enemies.includes(q) ? "E" : "N";
  }
  const temporalRel = (sp, sq) => [2, 3, 4, 10, 11, 12].includes(houseFrom(sp, sq)) ? "F" : "E";
  const COMPOUND = { FF: "Great Friend", FE: "Neutral", NF: "Friend", NE: "Enemy", EF: "Neutral", EE: "Great Enemy" };
  function compoundRel(p, q, d1) {
    if (p === q) return "Self";
    return COMPOUND[naturalRel(p, q) + temporalRel(d1[p], d1[q])];
  }
  const exaltSign = p => (p in NODE_EXALT ? NODE_EXALT[p] : EXALTATION[p][0]);
  const debilSign = p => (p in NODE_DEBIL ? NODE_DEBIL[p] : (EXALTATION[p][0] + 6) % 12);
  function dignity(p, sign, deg, d1, useMt = true) {
    if (sign === exaltSign(p)) {
      if (useMt && MOOLATRIKONA[p] && MOOLATRIKONA[p][0] === sign) {
        const mt = MOOLATRIKONA[p];
        if (p === "Mercury" && deg >= mt[1]) return deg < mt[2] ? "Moolatrikona" : "Own";
        if (p === "Moon" && deg >= mt[1]) return "Moolatrikona";
      }
      return "Exalted";
    }
    if (sign === debilSign(p)) return "Debilitated";
    if (useMt && MOOLATRIKONA[p]) {
      const [s, a, b] = MOOLATRIKONA[p];
      if (sign === s && deg >= a && deg < b) return "Moolatrikona";
    }
    const own = NODE_OWN[p] || OWN_SIGNS[p] || [];
    if (own.includes(sign)) return "Own";
    return compoundRel(p, SIGN_LORD[sign], d1);
  }
  const DIGNITY_SCORE = { Exalted: 5, Moolatrikona: 4, Own: 3.5, "Great Friend": 3, Friend: 2, Neutral: 1, Enemy: -1,
    "Great Enemy": -2, Debilitated: -4, Self: 3.5 };
  const SAPTAVARGAJA = { Moolatrikona: 45, Own: 30, "Great Friend": 22.5, Friend: 15, Neutral: 7.5, Enemy: 3.75,
    "Great Enemy": 1.875, Exalted: 30, Debilitated: 1.875 };
  function baladiAvastha(sign, deg) {
    const n = ["Bala (infant, 25% results)", "Kumara (youth, 50%)", "Yuva (adult, 100%)", "Vriddha (old, ~10%)", "Mrita (dead, ~0%)"];
    const i = Math.min(Math.floor(deg / 6), 4);
    return isOdd(sign) ? n[i] : n[4 - i];
  }
  function jagradadi(dig) {
    if (["Exalted", "Own", "Moolatrikona"].includes(dig)) return "Jagrat (awake - full results)";
    if (["Great Friend", "Friend", "Neutral"].includes(dig)) return "Swapna (dreaming - medium results)";
    return "Sushupti (sleeping - weak results)";
  }

  // ---------------------------------------------------------------- chart
  function nakshatraOf(lon) {
    lon = Astro.norm(lon);
    const idx = Math.floor(lon / NAK_SPAN) % 27;
    const pada = Math.floor((lon % NAK_SPAN) / PADA_SPAN) + 1;
    const [name, lord, deity, gana] = NAKSHATRAS[idx];
    return { index: idx, name, pada, lord, deity, gana, fraction_elapsed: (lon % NAK_SPAN) / NAK_SPAN };
  }
  const aspectedHouses = p => SPECIAL_ASPECTS[p] || [7];

  class Chart {
    /* birth: {name, y, mo, d, h, mi, s, tz, lat, lon, place, gender} */
    constructor(birth, settings) {
      this.birth = birth;
      this.settings = Object.assign(defaults(), settings || {});
      this.utc = Astro.localToUtc(birth.y, birth.mo, birth.d, birth.h, birth.mi, birth.s || 0, birth.tz);
      this.jd = Astro.dateToJd(this.utc);
      this.snap = Astro.snapshot(this.jd, birth.lat, birth.lon);
      this.sun = Astro.sunEvents(this.jd, birth.lat, birth.lon);
      this.asc = this.snap.asc;
      this.lagna = signOf(this.asc);
      this.lon = {}; this.sign = {}; this.house = {};
      for (const p of PLANETS) {
        this.lon[p] = this.snap.bodies[p].lon;
        this.sign[p] = signOf(this.lon[p]);
        this.house[p] = houseFrom(this.lagna, this.sign[p]);
      }
      this.moonSign = this.sign.Moon;
      this.d1 = { ...this.sign };
      this.vargas = {};
      for (const d of ALL_VARGAS) {
        const v = {};
        for (const p of PLANETS) v[p] = vargaSign(this.lon[p], d);
        v.Lagna = vargaSign(this.asc, d);
        this.vargas[d] = v;
      }
      this.dig = {};
      for (const p of PLANETS) this.dig[p] = dignity(p, this.sign[p], degIn(this.lon[p]), this.d1);
      this._asp = {};
    }
    lordOfHouse(h, from) { return SIGN_LORD[((from == null ? this.lagna : from) + h - 1) % 12]; }
    housesOwned(p, from) {
      const base = from == null ? this.lagna : from;
      const out = [];
      for (let h = 1; h <= 12; h++) if (SIGN_LORD[(base + h - 1) % 12] === p) out.push(h);
      return out;
    }
    occupants(h) { return PLANETS.filter(p => this.house[p] === h); }
    speed(p) { return this.snap.bodies[p].speed; }
    retro(p) { return p === "Rahu" || p === "Ketu" ? true : this.snap.bodies[p].speed < 0; }
    aspectsOf(p) {
      const out = [];
      for (const n of aspectedHouses(p)) {
        const th = ((this.house[p] + n - 2) % 12) + 1;
        out.push({ aspect: n, house: th, planets: this.occupants(th), primary: true });
      }
      if (p === "Rahu" || p === "Ketu") for (const n of [5, 9]) {
        const th = ((this.house[p] + n - 2) % 12) + 1;
        out.push({ aspect: n, house: th, planets: this.occupants(th), primary: false, note: "disputed node aspect (see variants.node_aspects)" });
      }
      return out;
    }
    aspectedBy(h, primaryOnly = false) {
      const key = h + ":" + primaryOnly;
      if (this._asp[key]) return this._asp[key];
      const res = [];
      for (const p of PLANETS) for (const a of this.aspectsOf(p))
        if (a.house === h && (a.primary || !primaryOnly)) res.push(a.primary ? p : `${p} (secondary)`);
      return (this._asp[key] = res);
    }
    planetAspectedBy(q, primaryOnly = true) {
      const nodes = ["Rahu", "Ketu"];
      return this.aspectedBy(this.house[q], primaryOnly).map(x => x.split(" ")[0])
        .filter(a => a !== q && !(nodes.includes(a) && nodes.includes(q)));
    }
    conjunct(p) { return PLANETS.filter(q => q !== p && this.sign[q] === this.sign[p]); }
    connected(p, q) {
      const w = [];
      if (this.sign[p] === this.sign[q]) w.push("conjunction");
      if (this.planetAspectedBy(p).includes(q)) w.push(`${q} aspects ${p}`);
      if (this.planetAspectedBy(q).includes(p)) w.push(`${p} aspects ${q}`);
      if (SIGN_LORD[this.sign[p]] === q && SIGN_LORD[this.sign[q]] === p) w.push("parivartana (sign exchange)");
      return w;
    }
    planetRow(p) {
      const b = this.snap.bodies[p], nak = nakshatraOf(b.lon), deg = degIn(b.lon);
      return {
        planet: p, longitude: round(b.lon, 4), sign: SIGNS[this.sign[p]], degree: fmtDms(deg), degree_decimal: round(deg, 3),
        house: this.house[p], house_from_moon: houseFrom(this.moonSign, this.sign[p]), nakshatra: nak.name, pada: nak.pada,
        nakshatra_lord: nak.lord, sign_lord: SIGN_LORD[this.sign[p]], retrograde: this.retro(p),
        speed_deg_per_day: round(b.speed, 4), dignity: this.dig[p], navamsa: SIGNS[this.vargas[9][p]],
        vargottama: this.vargas[9][p] === this.sign[p], owns_houses: this.housesOwned(p),
        baladi_avastha: baladiAvastha(this.sign[p], deg), jagradadi_avastha: jagradadi(this.dig[p]),
        conjunct: this.conjunct(p), aspected_by: this.planetAspectedBy(p),
      };
    }
    lagnaRow() {
      const nak = nakshatraOf(this.asc);
      return { sign: SIGNS[this.lagna], degree: fmtDms(degIn(this.asc)), longitude: round(this.asc, 4),
        lord: SIGN_LORD[this.lagna], nakshatra: nak.name, pada: nak.pada, nakshatra_lord: nak.lord,
        navamsa: SIGNS[this.vargas[9].Lagna] };
    }
    houseRows() {
      const rows = [];
      for (let h = 1; h <= 12; h++) {
        const s = (this.lagna + h - 1) % 12, lord = SIGN_LORD[s];
        rows.push({ house: h, sign: SIGNS[s], lord, lord_in_house: this.house[lord], lord_dignity: this.dig[lord],
          occupants: this.occupants(h), aspected_by: this.aspectedBy(h) });
      }
      return rows;
    }
    bhavaChalit() {
      const out = [];
      for (const p of PLANETS) {
        const rel = Astro.norm(this.lon[p] - this.asc + 15);
        const ch = Math.floor(rel / 30) + 1;
        if (ch !== this.house[p]) out.push({ planet: p, whole_sign_house: this.house[p], chalit_house: ch });
      }
      return out;
    }
  }

  // ---------------------------------------------------------------- functional nature, states
  const NB = ["Jupiter", "Venus", "Mercury", "Moon"];
  function functionalNature(c) {
    const out = {};
    for (const p of SEVEN) {
      const owned = c.housesOwned(p), notes = [];
      let score = 0;
      const isLL = owned.includes(1);
      const kendras = owned.filter(h => [4, 7, 10].includes(h)), trines = owned.filter(h => [5, 9].includes(h));
      const yk = kendras.length > 0 && trines.length > 0;
      for (const h of owned) {
        if ([1, 5, 9].includes(h)) score += 3;
        else if ([4, 7, 10].includes(h)) {
          if (NB.includes(p)) { score -= 1; notes.push(`kendradhipati dosha: natural benefic owning house ${h}`); }
        } else if ([3, 6, 11].includes(h)) score -= 2;
        else if (h === 8) {
          if (p === "Sun" || p === "Moon") notes.push("8th lordship blemish does not apply to Sun/Moon (BPHS 34)");
          else if (!isLL) score -= 2;
        }
      }
      if (owned.includes(2) || owned.includes(7)) notes.push("maraka (lord of 2nd/7th) - can bring health crises or endings in its periods");
      const verdict = isLL ? "Benefic (lagna lord - always auspicious)" : yk ? "Yogakaraka (owns kendra + trikona - best benefic)"
        : score > 0 ? "Benefic" : score < 0 ? "Malefic" : "Neutral (gives results by association/placement)";
      out[p] = { owns: owned, verdict, score, notes };
    }
    for (const node of ["Rahu", "Ketu"]) {
      const disp = SIGN_LORD[c.sign[node]];
      out[node] = { owns: [], verdict: `Acts like its dispositor ${disp} and conjunct planets`, dispositor: disp,
        dispositor_verdict: out[disp].verdict, score: out[disp].score,
        notes: ["Nodes give the results of the sign lord and of planets they join (BPHS 34/47)"] };
    }
    const bh = { Movable: 11, Fixed: 9, Dual: 7 }[MODALITY[c.lagna]];
    return { planets: out, badhaka_house: bh, badhaka_lord: c.lordOfHouse(bh),
      maraka_lords: [...new Set([c.lordOfHouse(2), c.lordOfHouse(7)])].sort(),
      yogakarakas: Object.keys(out).filter(p => out[p].verdict.startsWith("Yogakaraka")) };
  }
  function combustion(c) {
    const orbs = c.settings.combustion_orbs, out = {};
    for (const p of ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]) {
      const d = Math.abs(((c.lon[p] - c.lon.Sun + 540) % 360) - 180);
      const key = c.retro(p) && (p + "_retro") in orbs ? p + "_retro" : p;
      const orb = orbs[key];
      if (d <= orb) out[p] = { distance_from_sun: round(d, 2), orb, combust: true, deep: d <= orb / 2,
        note: p === "Mercury" ? "Mercury is combust in most charts; many authors treat its combustion as mild" : "" };
    }
    return out;
  }
  function gandanta(c) {
    const span = NAK_SPAN / 4, out = [];
    for (const [name, lon] of [["Lagna", c.asc], ...PLANETS.map(p => [p, c.lon[p]])]) {
      const s = signOf(lon), d = degIn(lon);
      if (([3, 7, 11].includes(s) && d >= 30 - span) || ([4, 8, 0].includes(s) && d <= span))
        out.push({ point: name, sign: SIGNS[s], degree: round(d, 2), note: "Gandanta: a knot between water and fire signs - weakness/turbulence for its significations" });
    }
    return out;
  }
  function planetCondition(c, comb, war, shad, func) {
    const out = {}, lost = new Set(war.map(w => w.loser));
    for (const p of PLANETS) {
      const plus = [], minus = [];
      const dig = c.dig[p], sc = DIGNITY_SCORE[dig] ?? 0;
      (sc < 0 ? minus : plus).push(`dignity: ${dig}`);
      if (c.vargas[9][p] === c.sign[p]) plus.push("vargottama (same sign in D1 and D9)");
      const nd = dignity(p, c.vargas[9][p], 0, c.d1, false);
      if (nd === "Exalted" || nd === "Own") plus.push(`navamsa dignity: ${nd}`);
      else if (nd === "Debilitated") minus.push("debilitated in navamsa");
      const h = c.house[p];
      if ([1, 4, 7, 10].includes(h)) plus.push(`in kendra (house ${h})`);
      if ([5, 9].includes(h)) plus.push(`in trikona (house ${h})`);
      if ([6, 8, 12].includes(h)) minus.push(`in dusthana (house ${h})`);
      if (comb[p]) minus.push(`combust (${pyNum(comb[p].distance_from_sun)}° from Sun)`);
      if (lost.has(p)) minus.push("defeated in planetary war");
      if (SEVEN.includes(p)) {
        if (c.retro(p) && p !== "Sun" && p !== "Moon") plus.push("retrograde: full chesta bala (BPHS); results often delayed or repeated");
        const r = shad.planets[p].ratio;
        (r >= 1 ? plus : minus).push(`shadbala ${pyNum(shad.planets[p].rupas)} rupas (${pyNum(r)}x required)`);
      }
      const av = baladiAvastha(c.sign[p], degIn(c.lon[p]));
      if (av.startsWith("Mrita") || av.startsWith("Vriddha")) minus.push(`baladi avastha ${av}`);
      else if (av.startsWith("Yuva")) plus.push(`baladi avastha ${av}`);
      const asp = c.planetAspectedBy(p);
      const ben = asp.filter(q => NATURAL_BENEFICS.includes(q)), mal = asp.filter(q => !NATURAL_BENEFICS.includes(q));
      if (ben.length) plus.push(`aspected by benefics ${pyList(ben)}`);
      if (mal.length) minus.push(`aspected by malefics ${pyList(mal)}`);
      const cm = c.conjunct(p).filter(q => ["Saturn", "Mars", "Rahu", "Ketu"].includes(q));
      if (cm.length) minus.push(`conjunct malefics ${pyList(cm)}`);
      out[p] = { strengths: plus, weaknesses: minus, net: plus.length - minus.length, functional: func.planets[p].verdict };
    }
    return out;
  }

  // ---------------------------------------------------------------- dasha
  const DAY = 86400000;
  const seqFrom = lord => { const i = DASHA_ORDER.indexOf(lord); return DASHA_ORDER.slice(i).concat(DASHA_ORDER.slice(0, i)); };
  function subPeriods(lord, start, lengthDays) {
    const out = []; let t = start;
    for (const sub of seqFrom(lord)) {
      const d = lengthDays * DASHA_YEARS[sub] / 120;
      out.push({ lord: sub, start: t, end: t + d * DAY });
      t += d * DAY;
    }
    return out;
  }
  function vimshottari(moonLon, birthMs, yearDays = 365.25) {
    const nak = Math.floor(Astro.norm(moonLon) / NAK_SPAN) % 27;
    const lord = DASHA_ORDER[nak % 9];
    const frac = (Astro.norm(moonLon) % NAK_SPAN) / NAK_SPAN;
    const start = birthMs - frac * DASHA_YEARS[lord] * yearDays * DAY;
    const mds = []; let t = start;
    for (const md of seqFrom(lord).concat(seqFrom(lord))) {
      const len = DASHA_YEARS[md] * yearDays;
      mds.push({ lord: md, start: t, end: t + len * DAY, length_days: len });
      t += len * DAY;
      if (t > birthMs + 125 * 365.25 * DAY) break;
    }
    return { birth_lord: lord, balance_years: round(DASHA_YEARS[lord] * (1 - frac), 4), mahadashas: mds, year_days: yearDays };
  }
  const antardashas = md => subPeriods(md.lord, md.start, md.length_days);
  const pratyantars = (md, ad) => subPeriods(ad.lord, ad.start, (ad.end - ad.start) / DAY);
  function runningDasha(v, when) {
    for (const md of v.mahadashas) if (md.start <= when && when < md.end)
      for (const ad of antardashas(md)) if (ad.start <= when && when < ad.end)
        for (const pd of pratyantars(md, ad)) if (pd.start <= when && when < pd.end) return { md, ad, pd };
    return null;
  }
  function periodsBetween(v, a, b) {
    const out = [];
    for (const md of v.mahadashas) {
      if (md.end < a || md.start > b) continue;
      for (const ad of antardashas(md)) {
        if (ad.end < a || ad.start > b) continue;
        out.push({ md: md.lord, ad: ad.lord, start: ad.start, end: ad.end });
      }
    }
    return out;
  }
  const fmtDate = ms => new Date(ms).toISOString().slice(0, 10);
  const fmtYm = ms => new Date(ms).toISOString().slice(0, 7);

  // ---------------------------------------------------------------- ashtakavarga
  const BAV_TABLE = {
    Sun: { Sun: [1, 2, 4, 7, 8, 9, 10, 11], Moon: [3, 6, 10, 11], Mars: [1, 2, 4, 7, 8, 9, 10, 11], Mercury: [3, 5, 6, 9, 10, 11, 12],
      Jupiter: [5, 6, 9, 11], Venus: [6, 7, 12], Saturn: [1, 2, 4, 7, 8, 9, 10, 11], Lagna: [3, 4, 6, 10, 11, 12] },
    Moon: { Sun: [3, 6, 7, 8, 10, 11], Moon: [1, 3, 6, 7, 10, 11], Mars: [2, 3, 5, 6, 9, 10, 11], Mercury: [1, 3, 4, 5, 7, 8, 10, 11],
      Jupiter: [1, 4, 7, 8, 10, 11, 12], Venus: [3, 4, 5, 7, 9, 10, 11], Saturn: [3, 5, 6, 11], Lagna: [3, 6, 10, 11] },
    Mars: { Sun: [3, 5, 6, 10, 11], Moon: [3, 6, 11], Mars: [1, 2, 4, 7, 8, 10, 11], Mercury: [3, 5, 6, 11], Jupiter: [6, 10, 11, 12],
      Venus: [6, 8, 11, 12], Saturn: [1, 4, 7, 8, 9, 10, 11], Lagna: [1, 3, 6, 10, 11] },
    Mercury: { Sun: [5, 6, 9, 11, 12], Moon: [2, 4, 6, 8, 10, 11], Mars: [1, 2, 4, 7, 8, 9, 10, 11], Mercury: [1, 3, 5, 6, 9, 10, 11, 12],
      Jupiter: [6, 8, 11, 12], Venus: [1, 2, 3, 4, 5, 8, 9, 11], Saturn: [1, 2, 4, 7, 8, 9, 10, 11], Lagna: [1, 2, 4, 6, 8, 10, 11] },
    Jupiter: { Sun: [1, 2, 3, 4, 7, 8, 9, 10, 11], Moon: [2, 5, 7, 9, 11], Mars: [1, 2, 4, 7, 8, 10, 11], Mercury: [1, 2, 4, 5, 6, 9, 10, 11],
      Jupiter: [1, 2, 3, 4, 7, 8, 10, 11], Venus: [2, 5, 6, 9, 10, 11], Saturn: [3, 5, 6, 12], Lagna: [1, 2, 4, 5, 6, 7, 9, 10, 11] },
    Venus: { Sun: [8, 11, 12], Moon: [1, 2, 3, 4, 5, 8, 9, 11, 12], Mars: [3, 5, 6, 9, 11, 12], Mercury: [3, 5, 6, 9, 11],
      Jupiter: [5, 8, 9, 10, 11], Venus: [1, 2, 3, 4, 5, 8, 9, 10, 11], Saturn: [3, 4, 5, 8, 9, 10, 11], Lagna: [1, 2, 3, 4, 5, 8, 9, 11] },
    Saturn: { Sun: [1, 2, 4, 7, 8, 10, 11], Moon: [3, 6, 11], Mars: [3, 5, 6, 10, 11, 12], Mercury: [6, 8, 9, 10, 11, 12],
      Jupiter: [5, 6, 11, 12], Venus: [6, 11, 12], Saturn: [3, 5, 6, 11], Lagna: [1, 3, 4, 6, 10, 11] },
  };
  function ashtakavarga(signs, lagna) {
    const pos = { ...signs, Lagna: lagna }, bav = {};
    for (const [planet, table] of Object.entries(BAV_TABLE)) {
      const row = Array(12).fill(0);
      for (const [contrib, houses] of Object.entries(table)) for (const h of houses) row[(pos[contrib] + h - 1) % 12] += 1;
      bav[planet] = row;
    }
    const sav = Array.from({ length: 12 }, (_, s) => Object.values(bav).reduce((a, r) => a + r[s], 0));
    return { bav, sav };
  }
  function interpretSav(sav, lagna) {
    const out = [];
    for (let h = 1; h <= 12; h++) {
      const b = sav[(lagna + h - 1) % 12];
      out.push({ house: h, bindus: b, quality: b >= 30 ? "strong" : b >= 28 ? "good" : b >= 25 ? "average" : "weak" });
    }
    return out;
  }

  // ---------------------------------------------------------------- shadbala
  const arc = (a, b) => { const d = Math.abs(a - b) % 360; return d > 180 ? 360 - d : d; };
  function sphutaDrishti(asp, fromLon, toLon) {
    const d = Astro.norm(toLon - fromLon);
    let v;
    if (d < 30 || d >= 300) v = 0;
    else if (d < 60) v = (d - 30) / 2;
    else if (d < 90) v = d - 60 + 15;
    else if (d < 120) v = (120 - d) / 2 + 30;
    else if (d < 150) v = 150 - d;
    else if (d < 180) v = (d - 150) * 2;
    else v = (300 - d) / 2;
    if (asp === "Mars" && ((d >= 90 && d < 120) || (d >= 210 && d < 240))) v += 15;
    else if (asp === "Jupiter" && ((d >= 120 && d < 150) || (d >= 240 && d < 270))) v += 30;
    else if (asp === "Saturn" && ((d >= 60 && d < 90) || (d >= 270 && d < 300))) v += 45;
    return Math.min(v, 60);
  }
  function saptavargaDignity(p, sign, deg, isD1, d1) {
    if (isD1) { const [s, a, b] = MOOLATRIKONA[p]; if (sign === s && deg >= a && deg < b) return "Moolatrikona"; }
    if (OWN_SIGNS[p].includes(sign)) return "Own";
    return compoundRel(p, SIGN_LORD[sign], d1);
  }
  function isBenefic(c, p) {
    if (p === "Jupiter" || p === "Venus") return true;
    if (p === "Moon") return Astro.norm(c.lon.Moon - c.lon.Sun) <= 180;
    if (p === "Mercury") return !c.conjunct("Mercury").some(q => ["Sun", "Mars", "Saturn", "Rahu", "Ketu"].includes(q));
    return false;
  }
  const WAR_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  function planetaryWar(c) {
    const out = [];
    WAR_PLANETS.forEach((a, i) => WAR_PLANETS.slice(i + 1).forEach(b => {
      if (arc(c.lon[a], c.lon[b]) < 1) {
        const la = c.snap.bodies[a].lat, lb = c.snap.bodies[b].lat;
        const [winner, loser] = la >= lb ? [a, b] : [b, a];
        const alt = [a, b].includes("Venus") ? "Venus" : winner;
        out.push({ planets: [a, b], separation: round(arc(c.lon[a], c.lon[b]), 3), winner, loser,
          variant_winner_by_brightness: alt, variants_agree: alt === winner,
          source: "Surya Siddhanta 7 (northern planet wins); brightness rule as variant" });
      }
    }));
    return out;
  }
  const KALI_EPOCH_JD = 588465.5;
  function shadbala(c) {
    const lon = c.lon, sun = c.sun;
    const elong = Astro.norm(lon.Moon - lon.Sun), pakshaArc = elong <= 180 ? elong : 360 - elong;
    const dayLen = sun.sunset - sun.sunrise, nightLen = sun.next_sunrise - sun.sunset;
    const midday = sun.sunrise + dayLen / 2;
    const distNoon = Math.abs(((((c.jd - midday + 0.5) % 1) + 1) % 1) - 0.5);
    const diurnal = 60 * (1 - distNoon / 0.5);
    let tribhagaLord;
    if (sun.is_day) tribhagaLord = ["Mercury", "Sun", "Saturn"][Math.min(Math.floor((c.jd - sun.sunrise) / (dayLen / 3)), 2)];
    else tribhagaLord = ["Moon", "Venus", "Mars"][Math.min(Math.floor((c.jd - sun.sunset) / (nightLen / 3)), 2)];
    const dayNum = Math.floor(sun.sunrise + 0.5 + c.birth.lon / 360);
    const ahargana = dayNum - Math.floor(KALI_EPOCH_JD + 0.5);
    const yearStart = dayNum - (ahargana % 360), monthStart = dayNum - (ahargana % 30);
    const abda = WEEKDAY_LORD[(yearStart + 1) % 7], masa = WEEKDAY_LORD[(monthStart + 1) % 7];
    const pre = {};
    for (const p of SEVEN) {
      const s = c.sign[p], deg = degIn(lon[p]), comp = {};
      const debilPoint = Astro.norm(EXALTATION[p][0] * 30 + EXALTATION[p][1] + 180);
      comp.uchcha = arc(lon[p], debilPoint) / 3;
      let sv = 0;
      for (const d of [1, 2, 3, 7, 9, 12, 30]) sv += SAPTAVARGAJA[saptavargaDignity(p, c.vargas[d][p], deg, d === 1, c.d1)];
      comp.saptavargaja = sv;
      const fem = p === "Moon" || p === "Venus";
      let oj = 0;
      for (const sg of [s, c.vargas[9][p]]) oj += (fem ? !isOdd(sg) : isOdd(sg)) ? 15 : 0;
      comp.ojayugma = oj;
      const h = c.house[p];
      comp.kendradi = [1, 4, 7, 10].includes(h) ? 60 : [2, 5, 8, 11].includes(h) ? 30 : 15;
      const dk = Math.floor(deg / 10);
      comp.drekkana = (GENDER[p] === "M" && dk === 0) || (GENDER[p] === "N" && dk === 1) || (GENDER[p] === "F" && dk === 2) ? 15 : 0;
      const sthana = Object.values(comp).reduce((a, b) => a + b, 0);
      const strong = { 1: c.asc, 4: Astro.norm(c.snap.mc + 180), 7: Astro.norm(c.asc + 180), 10: c.snap.mc }[DIG_BALA_HOUSE[p]];
      const dig = (180 - arc(lon[p], strong)) / 3;
      const kala = {};
      kala.nathonnata = p === "Mercury" ? 60 : ["Sun", "Jupiter", "Venus"].includes(p) ? diurnal : 60 - diurnal;
      const pk = isBenefic(c, p) ? pakshaArc / 3 : 60 - pakshaArc / 3;
      kala.paksha = p === "Moon" ? pk * 2 : pk;
      kala.tribhaga = p === "Jupiter" || p === tribhagaLord ? 60 : 0;
      kala.abda = p === abda ? 15 : 0;
      kala.masa = p === masa ? 30 : 0;
      kala.vara = p === sun.vara_lord ? 45 : 0;
      kala.hora = p === sun.hora_lord ? 60 : 0;
      const decl = c.snap.bodies[p].decl;
      const ay = p === "Moon" || p === "Saturn" ? (24 - decl) / 48 * 60 : p === "Mercury" ? (24 + Math.abs(decl)) / 48 * 60 : (24 + decl) / 48 * 60;
      kala.ayana = p === "Sun" ? ay * 2 : ay;
      let chesta;
      if (p === "Sun") chesta = kala.ayana / 2;
      else if (p === "Moon") chesta = pakshaArc / 3;
      else {
        const r = c.speed(p) / MEAN_SPEED[p];
        chesta = r < -0.1 ? 60 : r < 0 ? 30 : r < 0.1 ? 15 : r < 0.5 ? 15 : r < 0.9 ? 30 : r < 1.1 ? 7.5 : r < 1.5 ? 45 : 30;
      }
      pre[p] = { sthana: comp, sthana_total: sthana, dig, kala, kala_total: Object.values(kala).reduce((a, b) => a + b, 0),
        chesta, naisargika: NAISARGIKA[p] };
    }
    for (const p of SEVEN) {
      let tot = 0;
      for (const q of SEVEN) if (q !== p) { const v = sphutaDrishti(q, lon[q], lon[p]); tot += isBenefic(c, q) ? v : -v; }
      pre[p].drik = tot / 4;
    }
    for (const w of planetaryWar(c)) {
      const sum = x => pre[x].sthana_total + pre[x].dig + pre[x].kala_total;
      const diff = Math.abs(sum(w.winner) - sum(w.loser));
      pre[w.winner].kala.yuddha = diff; pre[w.loser].kala.yuddha = -diff;
      for (const x of [w.winner, w.loser]) pre[x].kala_total = Object.values(pre[x].kala).reduce((a, b) => a + b, 0);
    }
    const res = {};
    for (const p of SEVEN) {
      const r = pre[p];
      const total = r.sthana_total + r.dig + r.kala_total + r.chesta + r.naisargika + r.drik;
      const rupas = total / 60, uch = r.sthana.uchcha;
      const rd = o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, round(v, 2)]));
      res[p] = { sthana: round(r.sthana_total, 2), sthana_parts: rd(r.sthana), dig: round(r.dig, 2), kala: round(r.kala_total, 2),
        kala_parts: rd(r.kala), chesta: round(r.chesta, 2), naisargika: r.naisargika, drik: round(r.drik, 2),
        total_virupas: round(total, 1), rupas: round(rupas, 2), required_rupas: SHADBALA_REQUIRED[p],
        ratio: round(rupas / SHADBALA_REQUIRED[p], 2), verdict: rupas >= SHADBALA_REQUIRED[p] ? "strong" : "weak",
        ishta_phala: round(Math.sqrt(Math.max(uch, 0) * Math.max(r.chesta, 0)), 1),
        kashta_phala: round(Math.sqrt(Math.max(60 - uch, 0) * Math.max(60 - r.chesta, 0)), 1) };
    }
    return { planets: res, rank_by_ratio: [...SEVEN].sort((a, b) => res[b].ratio - res[a].ratio),
      approximations: [
        "Chesta bala for Mars-Saturn uses motion categories from the current speed (vakra, sama, chara...), not the full cheshta-kendra computation.",
        "Abda (year) and masa (month) lords use 360/30-day counts from the Kali epoch.",
        "Yuddha bala uses the difference of the two planets' other balas.",
        "Dig bala uses the exact ascendant/midheaven degrees (not bhava madhya of a quadrant system).",
      ], abda_lord: abda, masa_lord: masa, vara_lord: sun.vara_lord, hora_lord: sun.hora_lord };
  }

  Object.assign(J, {
    PLANETS, SEVEN, SIGNS, SIGN_LORD, MODALITY, isOdd, OWN_SIGNS, EXALTATION, MOOLATRIKONA, NATURAL_FRIENDS, NATURAL_BENEFICS,
    NAKSHATRAS, NAK_SPAN, GANDMOOL, DASHA_ORDER, DASHA_YEARS, SPECIAL_ASPECTS, BHAVA_MEANING, VARIANTS, VARGA_NAMES, ALL_VARGAS,
    signOf, degIn, houseFrom, round, pyList, pyNum, fmtDms, vargaSign, naturalRel, compoundRel, exaltSign, debilSign, dignity, DIGNITY_SCORE,
    baladiAvastha, jagradadi, nakshatraOf, Chart, functionalNature, combustion, gandanta, planetCondition, DAY, vimshottari,
    antardashas, pratyantars, runningDasha, periodsBetween, fmtDate, fmtYm, BAV_TABLE, ashtakavarga, interpretSav,
    sphutaDrishti, planetaryWar, shadbala, defaults,
  });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
