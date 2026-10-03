/* Cross-area views so a reading is never done one area at a time:
   - planet_map: each planet -> every area it runs, its body parts, and when its dashas run
   - life_chapters: each mahadasha as a chapter of life with the areas it switches on
   - timeline: every antardasha from 10 years back to 10 years ahead with ALL areas it activates
   - slow_transits: Saturn / Jupiter / Rahu-Ketu sign changes with houses and body regions
   - upcoming_5y: medium/high windows of every area in the next 5 years, in date order */
(function (root) {
  const J = root.J || require("./engine-explain.js");
  const { Astro, PLANETS, SIGNS, houseFrom, signOf, DAY, fmtYm, vimshottari, periodsBetween, AREAS, significators } = J;

  const BODY_PLANET = {
    Sun: "heart, eyes, bones, vitality", Moon: "mind, sleep, body fluids, hormones and menstrual cycle, chest",
    Mars: "blood, muscles, injuries, cuts, burns, surgery, fever", Mercury: "skin, nerves, speech, lungs, hands",
    Jupiter: "liver, fat, sugar levels, ears", Venus: "reproductive system, kidneys, throat, hormones, feet (as 12th-house lord)",
    Saturn: "bones, joints, ligaments, knees, legs, teeth, chronic problems", Rahu: "allergies, poisoning, unclear illnesses, anxiety",
    Ketu: "wounds, infections, sudden injuries, nerve issues",
  };
  const BODY_SIGN = ["head", "face and throat", "shoulders, arms and lungs", "chest and stomach", "heart and upper back",
    "intestines and digestion", "lower back and kidneys", "reproductive organs", "hips and thighs", "knees and joints",
    "calves, ankles and circulation", "feet"];
  const AREA_SHORT = Object.fromEntries(Object.entries(AREAS).map(([k, a]) => [k, a.label.split(" (")[0]]));
  const NODE_NOTES = {
    12: "foreign lands, multinational work, life away from home", 10: "unusual or technology-driven career, sudden rise",
    7: "unconventional partner or foreign connection in marriage", 1: "restless, ambitious personality",
    4: "moving homes, foreign residence", 9: "foreign travel, unorthodox beliefs", 11: "large gains through networks/technology",
    5: "unconventional romance or studies", 6: "beats competition, health needs watching", 8: "sudden events, research, hidden matters",
    2: "unusual speech/food habits, money through unusual means", 3: "bold communication, media, short trips",
  };

  function areaOwners(c) {
    const out = {};
    for (const [k, a] of Object.entries(AREAS)) {
      const main = significators(c, [a.main]);
      const kar = a.karaka_m ? (c.birth.gender === "F" ? a.karaka_f : a.karaka_m) : a.karaka;
      out[k] = { main, kar };
    }
    return out;
  }
  /* How strongly planet p runs each area: lord of the area's house or sitting in it = 3, natural karaka = 2,
     aspect / joined with the lord = 1, in the lord's nakshatra / node acting for a significator = 0.5.
     Only strong ties (score >= 2) count, so the map shows real links, not everything. */
  function tieScore(p, o) {
    let sc = o.kar === p ? 2 : 0;
    for (const why of o.main[p] || []) {
      if (/^lord of|^occupies/.test(why)) sc += 3;
      else if (/^in nakshatra|^dispositor/.test(why)) sc += 0.5;
      else sc += 1;
    }
    return sc;
  }
  function areasOf(p, owners, min = 2) {
    return Object.entries(owners).map(([k, o]) => [k, tieScore(p, o)]).filter(([, sc]) => sc >= min)
      .sort((a, b) => b[1] - a[1]).map(([k]) => k);
  }

  function insight(D, c, nowMs = Date.now()) {
    const owners = areaOwners(c);
    const v = vimshottari(c.lon.Moon, c.utc.getTime(), c.settings.dasha_year);
    // planet map
    const planet_map = {};
    for (const p of PLANETS) {
      const row = D.planets.find(x => x.planet === p);
      const mds = v.mahadashas.filter(m => m.lord === p).map(m => `${fmtYm(m.start)} to ${fmtYm(m.end)}`);
      planet_map[p] = { runs_areas: areasOf(p, owners).map(a => AREA_SHORT[a]), house: row.house, owns: row.owns_houses,
        sign: row.sign, dignity: row.dignity, body: BODY_PLANET[p], mahadasha_years: mds,
        condition_net: D.planet_condition[p].net, functional: D.functional_nature.planets[p].verdict,
        note: (p === "Rahu" || p === "Ketu") ? NODE_NOTES[row.house] || "" : "" };
    }
    // life chapters
    const birthMs = c.utc.getTime(), age = t => Math.round(((t - birthMs) / DAY / 365.25) * 10) / 10;
    const life_chapters = D.vimshottari.mahadashas.filter(m => age(Date.parse(m.start)) < 100).map(m => {
      const pm = planet_map[m.lord];
      return { mahadasha: m.lord, from: m.start.slice(0, 7), to: m.end.slice(0, 7), age_from: Math.max(0, age(Date.parse(m.start))),
        age_to: age(Date.parse(m.end)), tone: m.plain.tone, themes: m.plain.text, switches_on: pm.runs_areas,
        node_note: pm.note, is_current: Date.parse(m.start) <= nowMs && nowMs < Date.parse(m.end) };
    });
    // timeline of antardashas, all areas at once
    const timeline = periodsBetween(v, nowMs - 10 * 365.25 * DAY, nowMs + 10 * 365.25 * DAY).map(per => {
      const ad = areasOf(per.ad, owners).map(a => AREA_SHORT[a]);
      return { from: fmtYm(per.start), to: fmtYm(per.end), dasha: `${per.md}/${per.ad}`, areas_switched_on: ad,
        body_watch: BODY_PLANET[per.ad], is_current: per.start <= nowMs && nowMs < per.end, is_past: per.end < nowMs };
    });
    // slow transits: sign changes, 10 years back to 10 years ahead
    const slow_transits = [];
    for (const p of ["Saturn", "Jupiter", "Rahu"]) {
      let prev = null, startT = null;
      const step = 10 * DAY, t0 = nowMs - 10 * 365.25 * DAY, t1 = nowMs + 10 * 365.25 * DAY;
      const spans = [];
      for (let t = t0; t <= t1; t += step) {
        const s = signOf(Astro.siderealLon(p, Astro.dateToJd(new Date(t))));
        if (s !== prev) { if (prev !== null) spans.push([prev, startT, t]); prev = s; startT = t; }
      }
      spans.push([prev, startT, t1]);
      const merged = [];
      for (const sp of spans) { // fold short retrograde dips back into the main stay
        const last = merged[merged.length - 1];
        if (last && last[0] === sp[0]) last[2] = sp[2];
        else if (sp[2] - sp[1] < 100 * DAY && merged.length) merged[merged.length - 1][2] = sp[2];
        else merged.push(sp.slice());
      }
      for (const [s, a, b] of merged) {
        const hm = houseFrom(c.moonSign, s), hl = houseFrom(c.lagna, s);
        const good = (J.GOCHAR[p] || {})[hm] !== undefined;
        const row = { planet: p, sign: SIGNS[s], from: fmtYm(a), to: fmtYm(b), house_from_lagna: hl, house_from_moon: hm,
          body_region: BODY_SIGN[s], favourable_from_moon: good, is_past: b < nowMs, is_current: a <= nowMs && nowMs < b };
        if (p === "Rahu") {
          slow_transits.push({ ...row, planet: "Rahu" });
          const ks = (s + 6) % 12;
          slow_transits.push({ planet: "Ketu", sign: SIGNS[ks], from: row.from, to: row.to, house_from_lagna: houseFrom(c.lagna, ks),
            house_from_moon: houseFrom(c.moonSign, ks), body_region: BODY_SIGN[ks],
            favourable_from_moon: [3, 6, 11].includes(houseFrom(c.moonSign, ks)), is_past: row.is_past, is_current: row.is_current });
        } else slow_transits.push(row);
      }
    }
    // upcoming 5 years across all areas
    const until = fmtYm(nowMs + 5 * 365.25 * DAY), nowYm = fmtYm(nowMs);
    const upcoming_5y = [];
    for (const [k, a] of Object.entries(D.life_areas)) for (const w of a.timing.windows)
      if (w.end >= nowYm && w.start <= until && !/^low/.test(w.confidence))
        upcoming_5y.push({ from: w.start, to: w.end, area: AREA_SHORT[k], confidence: w.confidence.split(" ")[0], dasha: `${w.md}/${w.ad}` });
    upcoming_5y.sort((x, y) => (x.from < y.from ? -1 : x.from > y.from ? 1 : 0));
    // physical meaning of afflictions
    for (const p of PLANETS) D.planet_condition[p].body = BODY_PLANET[p];
    Object.assign(D, { planet_map, life_chapters, timeline, slow_transits, upcoming_5y });
    return D;
  }

  Object.assign(J, { insight, BODY_PLANET, BODY_SIGN });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
