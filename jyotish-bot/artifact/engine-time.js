/* Transits, life-area timing, rectification and the full dossier (port of transits.py, timing.py, dossier.py). */
(function (root) {
  const J = root.J || require("./engine-rules.js");
  const { Astro, PLANETS, SIGNS, SIGN_LORD, SPECIAL_ASPECTS, NATURAL_BENEFICS, houseFrom, signOf, pyList, round, DAY,
    dignity, DIGNITY_SCORE, nakshatraOf, vimshottari, runningDasha, periodsBetween, antardashas, fmtDate, fmtYm } = J;

  // ---------------------------------------------------------------- transits
  const GOCHAR = {
    Sun: { 3: 9, 6: 12, 10: 4, 11: 5 }, Moon: { 1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8 }, Mars: { 3: 12, 6: 9, 11: 5 },
    Mercury: { 2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12 }, Jupiter: { 2: 12, 5: 4, 7: 3, 9: 10, 11: 8 },
    Venus: { 1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3 }, Saturn: { 3: 12, 6: 9, 11: 5 },
    Rahu: { 3: 12, 6: 9, 11: 5 }, Ketu: { 3: 12, 6: 9, 11: 5 },
  };
  const noVedha = (a, b) => (a === "Sun" && b === "Saturn") || (a === "Saturn" && b === "Sun") ||
    (a === "Moon" && b === "Mercury") || (a === "Mercury" && b === "Moon");
  function influenced(base, sign, planet) {
    const h = houseFrom(base, sign), out = new Set([h]);
    for (const n of SPECIAL_ASPECTS[planet] || [7]) out.add(((h + n - 2) % 12) + 1);
    return out;
  }
  function doubleTransitHouses(lagna, ts) {
    const j = influenced(lagna, ts.Jupiter, "Jupiter"), s = influenced(lagna, ts.Saturn, "Saturn");
    return [...j].filter(x => s.has(x)).sort((a, b) => a - b);
  }
  function transitReport(c, whenMs, av) {
    const snap = Astro.snapshot(Astro.dateToJd(new Date(whenMs)));
    const M = c.moonSign, ts = {};
    for (const p of PLANETS) ts[p] = signOf(snap.bodies[p].lon);
    const rows = PLANETS.map(p => {
      const s = ts[p], hm = houseFrom(M, s), good = hm in GOCHAR[p];
      const vedhaBy = good ? PLANETS.filter(q => q !== p && houseFrom(M, ts[q]) === GOCHAR[p][hm] && !noVedha(p, q)) : [];
      const bindus = av.bav[p] ? av.bav[p][s] : null;
      let verdict = good && !vedhaBy.length ? "favourable" : good ? "favourable but obstructed (vedha)" : "unfavourable";
      if (bindus != null) verdict += `; ${bindus} bindus in own BAV (${bindus >= 4 ? "supports" : "weakens"})`;
      return { planet: p, sign: SIGNS[s], degree: round(snap.bodies[p].lon % 30, 2), retrograde: snap.bodies[p].speed < 0,
        house_from_lagna: houseFrom(c.lagna, s), house_from_moon: hm, sav_bindus_of_sign: av.sav[s], verdict, vedha_by: vedhaBy,
        over_natal: PLANETS.filter(q => c.sign[q] === s) };
    });
    const sat = houseFrom(M, ts.Saturn);
    const sade = { 12: "Sade Sati phase 1 (rising) - expenses, restlessness", 1: "Sade Sati phase 2 (peak) - pressure on mind/body, hard lessons",
      2: "Sade Sati phase 3 (setting) - finances/family strain easing", 4: "Kantaka/Ardhashtama Shani (4th from Moon) - home/peace disturbed",
      8: "Ashtama Shani (8th from Moon) - obstacles, health, sudden setbacks" }[sat] || null;
    return { date: fmtDate(whenMs), planets: rows, saturn_from_moon: sat, sade_sati_or_dhaiya: sade,
      double_transit_houses_from_lagna: doubleTransitHouses(c.lagna, ts) };
  }
  function sadeSatiPeriods(c, startMs, years = 100) {
    const jd0 = Astro.dateToJd(new Date(startMs)), M = c.moonSign, step = 5, n = Math.floor(years * 365.25 / step);
    const spans = []; let cur = null, curStart = null;
    for (let i = 0; i <= n; i++) {
      const jd = jd0 + i * step, h = houseFrom(M, signOf(Astro.siderealLon("Saturn", jd)));
      const tag = [12, 1, 2].includes(h) ? "Sade Sati" : h === 8 ? "Ashtama Shani" : h === 4 ? "Kantaka Shani" : null;
      if (tag !== cur || i === n) { if (cur) spans.push([cur, curStart, jd]); cur = tag; curStart = jd; }
    }
    const merged = [];
    for (const sp of spans) {
      const last = merged[merged.length - 1];
      if (last && last[0] === sp[0] && sp[1] - last[2] < 400) last[2] = sp[2]; else merged.push(sp);
    }
    const f = jd => Astro.jdToDate(jd).toISOString().slice(0, 7);
    return merged.map(([t, a, b]) => ({ type: t, start: f(a), end: f(b) }));
  }

  // ---------------------------------------------------------------- timing
  const AREAS = {
    marriage: { houses: [7, 2, 11], main: 7, karaka_m: "Venus", karaka_f: "Jupiter", varga: 9, label: "Marriage / spouse" },
    career: { houses: [10, 6, 11], main: 10, karaka: "Saturn", varga: 10, label: "Career / job / status" },
    wealth: { houses: [2, 11, 5, 9], main: 11, karaka: "Jupiter", varga: 2, label: "Money / gains" },
    children: { houses: [5, 2, 11], main: 5, karaka: "Jupiter", varga: 7, label: "Children" },
    education: { houses: [4, 5, 9], main: 5, karaka: "Mercury", varga: 24, label: "Education" },
    property: { houses: [4, 11, 2], main: 4, karaka: "Mars", varga: 4, label: "Property / home / vehicle" },
    foreign: { houses: [12, 9, 7, 3], main: 12, karaka: "Rahu", varga: 1, label: "Foreign travel / settlement" },
    health: { houses: [1, 6, 8, 12], main: 1, karaka: "Sun", varga: 1, label: "Health crises (6/8/12, marakas)", adverse: true },
    father: { houses: [9, 10], main: 9, karaka: "Sun", varga: 12, label: "Father" },
    mother: { houses: [4], main: 4, karaka: "Moon", varga: 12, label: "Mother" },
    siblings: { houses: [3, 11], main: 3, karaka: "Mars", varga: 3, label: "Siblings" },
    mind: { houses: [4, 1, 5, 8], main: 4, karaka: "Moon", varga: 1, label: "Mind / emotional stability (Moon, 4th, 5th)", adverse: false },
    govt_authority: { houses: [10, 9, 1, 11], main: 10, karaka: "Sun", varga: 10, label: "Government job / authority / fame" },
    accidents_surgery: { houses: [8, 6, 1], main: 8, karaka: "Mars", varga: 1, label: "Accidents / surgery / sudden events", adverse: true },
    love: { houses: [5, 7, 11], main: 5, karaka: "Venus", varga: 9, label: "Love & relationships (romance, dating, break-ups)" },
    spirituality: { houses: [9, 12, 5], main: 12, karaka: "Ketu", varga: 20, label: "Spiritual growth" },
    litigation: { houses: [6, 8, 12], main: 6, karaka: "Mars", varga: 1, label: "Disputes / debts / enemies", adverse: true },
  };
  const karakaOf = (c, s) => s.karaka_m ? (c.birth.gender === "F" ? s.karaka_f : s.karaka_m) : s.karaka;
  function significators(c, houses) {
    const sig = {};
    const add = (p, why) => { sig[p] = sig[p] || []; if (!sig[p].includes(why)) sig[p].push(why); };
    for (const h of houses) {
      const lord = c.lordOfHouse(h);
      add(lord, `lord of ${h}`);
      for (const p of c.occupants(h)) add(p, `occupies ${h}`);
      for (const p of c.aspectedBy(h, true)) add(p, `aspects ${h}`);
      for (const p of c.conjunct(lord)) add(p, `with lord of ${h}`);
    }
    const core = Object.keys(sig);
    for (const p of PLANETS) { const nl = nakshatraOf(c.lon[p]).lord; if (core.includes(nl) && !sig[p]) add(p, `in nakshatra of ${nl}`); }
    for (const node of ["Rahu", "Ketu"]) { const d = SIGN_LORD[c.sign[node]]; if (core.includes(d)) add(node, `dispositor ${d} is a significator`); }
    return sig;
  }
  function promise(c, area, av, cond) {
    const spec = AREAS[area], h = spec.main, lord = c.lordOfHouse(h), kar = karakaOf(c, spec), plus = [], minus = [];
    const occ = c.occupants(h);
    for (const p of occ) (NATURAL_BENEFICS.includes(p) ? plus : minus).push(`${p} occupies house ${h}`);
    for (const p of c.aspectedBy(h, true)) if (!occ.includes(p)) (NATURAL_BENEFICS.includes(p) ? plus : minus).push(`${p} aspects house ${h}`);
    const ds = DIGNITY_SCORE[c.dig[lord]] ?? 0;
    (ds > 0 ? plus : minus).push(`house lord ${lord} is ${c.dig[lord]} in house ${c.house[lord]}`);
    if ([6, 8, 12].includes(c.house[lord]) && ![6, 8, 12].includes(h)) minus.push(`house lord ${lord} sits in dusthana ${c.house[lord]}`);
    if ([1, 4, 5, 7, 9, 10].includes(c.house[lord])) plus.push(`house lord ${lord} in kendra/trikona`);
    (cond[kar].net >= 0 ? plus : minus).push(`karaka ${kar}: ${cond[kar].strengths.length} strengths vs ${cond[kar].weaknesses.length} weaknesses`);
    const sav = av.sav[(c.lagna + h - 1) % 12];
    if (sav >= 28) plus.push(`SAV bindus in house ${h}: ${sav} (good)`); else if (sav < 25) minus.push(`SAV bindus in house ${h}: ${sav} (weak)`);
    const d = spec.varga;
    if (d !== 1) {
      const vs = c.vargas[d][lord], vd = dignity(lord, vs, 0, c.d1, false);
      ((DIGNITY_SCORE[vd] ?? 0) > 0 ? plus : minus).push(`in D${d}, house lord ${lord} is in ${SIGNS[vs]} (${vd})`);
      const vh = houseFrom(c.vargas[d].Lagna, vs);
      ([6, 8, 12].includes(vh) ? minus : plus).push(`in D${d}, house lord falls in house ${vh} from D${d} lagna`);
      const kd = dignity(kar, c.vargas[d][kar], 0, c.d1, false);
      ((DIGNITY_SCORE[kd] ?? 0) > 0 ? plus : minus).push(`in D${d}, karaka ${kar} is ${kd}`);
    }
    const hm = (c.moonSign + h - 1) % 12, malM = PLANETS.filter(p => c.sign[p] === hm && !NATURAL_BENEFICS.includes(p));
    if (malM.length) minus.push(`malefics ${pyList(malM)} in house ${h} from Moon`);
    const score = plus.length - minus.length;
    let verdict = score >= 3 ? "strong" : score >= 0 ? "moderate" : score >= -3 ? "weak" : "very weak";
    if (spec.adverse) verdict = score >= 0 ? `${verdict} protection` : `${verdict} protection - vulnerable area`;
    return { area: spec.label, house: h, lord, karaka: kar, favourable: plus, unfavourable: minus, score, verdict };
  }
  function eventWindows(c, area, startMs, endMs, top = 8) {
    const spec = AREAS[area], main = spec.main, sig = significators(c, spec.houses), mainSig = significators(c, [main]);
    const kar = karakaOf(c, spec), v = vimshottari(c.lon.Moon, c.utc.getTime(), c.settings.dasha_year);
    const lord = c.lordOfHouse(main), lordSign = c.sign[lord], mainSign = (c.lagna + main - 1) % 12;
    const weight = p => (mainSig[p] ? 2 : sig[p] ? 1 : 0) + (p === kar ? 1 : 0);
    const jupBav = J.ashtakavarga(c.sign, c.lagna).bav.Jupiter[mainSign];
    const windows = [];
    const lordH = houseFrom(c.lagna, lordSign);
    for (const per of periodsBetween(v, startMs, endMs)) {
      const wm = weight(per.md), wa = weight(per.ad);
      if (wm + wa < 2 || (wa === 0 && wm < 3)) continue;
      const a = Math.max(per.start, startMs), b = Math.min(per.end, endMs);
      for (let t = a; t < b; t += 30 * DAY) {
        const jd = Astro.dateToJd(new Date(t));
        const jS = signOf(Astro.siderealLon("Jupiter", jd)), sS = signOf(Astro.siderealLon("Saturn", jd));
        const jh = influenced(c.lagna, jS, "Jupiter"), sh = influenced(c.lagna, sS, "Saturn");
        const dtHouse = jh.has(main) && sh.has(main), dtLord = jh.has(lordH) && sh.has(lordH);
        const desc = p => (sig[p] || (p === kar ? ["karaka"] : [])).join(", ");
        const factors = [`MD ${per.md} (${desc(per.md)})`, `AD ${per.ad} (${desc(per.ad)})`];
        let score = wm + wa;
        const run = runningDasha(v, t);
        if (run && weight(run.pd.lord) > 0) { score += 0.5 * weight(run.pd.lord); factors.push(`PD ${run.pd.lord} also a significator`); }
        if (dtHouse) { score += 2; factors.push(`double transit (Jupiter+Saturn) on house ${main}`); }
        if (dtLord) { score += 1.5; factors.push(`double transit on house of lord ${lord} (${lordH})`); }
        if (houseFrom(c.lagna, jS) === main || jS === lordSign) { score += 1; factors.push("Jupiter transits the house or its lord's sign"); }
        if (jupBav >= 5) { score += 0.5; factors.push(`Jupiter BAV ${jupBav} bindus in house ${main}`); }
        windows.push({ start: t, md: per.md, ad: per.ad, score: round(score, 1), factors, double_transit: dtHouse || dtLord });
      }
    }
    const merged = [];
    for (const w of windows) {
      const last = merged[merged.length - 1];
      if (last && last.md === w.md && last.ad === w.ad && last.double_transit === w.double_transit && Math.floor((w.start - last.end) / DAY) <= 31) {
        last.end = w.start + 30 * DAY;
        if (w.score > last.score) { last.score = w.score; last.factors = w.factors; last.peak = w.start; }
      } else merged.push({ ...w, end: w.start + 30 * DAY, peak: w.start });
    }
    for (const m of merged) m.confidence = m.double_transit && m.score >= 6 ? "high (dasha + double transit + support)"
      : m.double_transit || m.score >= 5 ? "medium" : "low (dasha only)";
    const ranked = merged.sort((x, y) => y.score - x.score || x.start - y.start).slice(0, top);
    for (const r of ranked) { r.start = fmtYm(r.start); r.end = fmtYm(r.end); r.peak = fmtYm(r.peak); }
    return { area: spec.label, significators: sig, karaka: kar, windows: ranked,
      method: "score = dasha significance (MD+AD) + Jupiter/Saturn double transit on house and lord + Jupiter transit + ashtakavarga. A window is 'high' only when dasha AND double transit agree." };
  }
  function marakaPeriods(c, startMs, endMs) {
    const primary = new Set([c.lordOfHouse(2), c.lordOfHouse(7), ...c.occupants(2), ...c.occupants(7)]);
    const secondary = new Set([c.lordOfHouse(8), c.lordOfHouse(12), c.lordOfHouse(6)]);
    const v = vimshottari(c.lon.Moon, c.utc.getTime(), c.settings.dasha_year), out = [];
    for (const per of periodsBetween(v, startMs, endMs)) {
      const tags = [];
      for (const [role, l] of [["MD", per.md], ["AD", per.ad]]) {
        if (primary.has(l)) tags.push(`${role} ${l} = maraka`); else if (secondary.has(l)) tags.push(`${role} ${l} = 6/8/12 lord`);
      }
      if (tags.length === 2) out.push({ md: per.md, ad: per.ad, start: fmtDate(per.start), end: fmtDate(per.end), why: tags });
    }
    return out;
  }
  function shiftBirth(b, minutes) {
    const d = new Date(Date.UTC(b.y, b.mo - 1, b.d, b.h, b.mi, b.s || 0) + minutes * 60000);
    return { ...b, y: d.getUTCFullYear(), mo: d.getUTCMonth() + 1, d: d.getUTCDate(), h: d.getUTCHours(), mi: d.getUTCMinutes(), s: d.getUTCSeconds() };
  }
  function sensitivity(birth, settings, minutes = 30) {
    const keys = c => ({ Lagna: SIGNS[c.lagna], "D9 Lagna": SIGNS[c.vargas[9].Lagna], "D10 Lagna": SIGNS[c.vargas[10].Lagna],
      "D7 Lagna": SIGNS[c.vargas[7].Lagna], "D60 Lagna": SIGNS[c.vargas[60].Lagna],
      "Moon pada": `${nakshatraOf(c.lon.Moon).name}-${nakshatraOf(c.lon.Moon).pada}` });
    const b0 = keys(new J.Chart(birth, settings)), changes = Object.fromEntries(Object.keys(b0).map(k => [k, []]));
    for (let m = -minutes; m <= minutes; m++) {
      if (m === 0) continue;
      const k = keys(new J.Chart(shiftBirth(birth, m), settings));
      for (const [key, val] of Object.entries(k)) if (val !== b0[key]) changes[key].push(m);
    }
    const out = {};
    for (const [k, ms] of Object.entries(changes)) {
      const before = ms.filter(m => m < 0), after = ms.filter(m => m > 0);
      const from = before.length ? Math.max(...before) + 1 : -minutes, to = after.length ? Math.min(...after) - 1 : minutes;
      const span = to - from;
      out[k] = { value: b0[k], stable_from_minutes: from, stable_to_minutes: to,
        reliability: span >= 2 * minutes ? "reliable" : span > 8 ? "time-sensitive" : "highly time-sensitive - verify birth time" };
    }
    const c0 = new J.Chart(birth, settings), near = [];
    for (const p of PLANETS) {
      const off = (c0.lon[p] % (J.NAK_SPAN / 4)), d = Math.min(off, J.NAK_SPAN / 4 - off);
      if (d < 0.01) near.push(`${p} is within ${Math.round(d * 3600)}" of a pada/navamsa boundary - its D9 sign and pada could flip with tiny changes in calculation`);
    }
    return { window_minutes: minutes, points: out, boundary_planets: near,
      limits: "Rectification can only narrow the time using known life events; with an uncertain time, D9 within a few minutes and D60 within seconds are unreliable, and so are judgements that rest on them." };
  }
  function rectifyByEvents(birth, settings, events, minutes = 60, step = 2) {
    const res = [];
    for (let m = -minutes; m <= minutes; m += step) {
      const b = shiftBirth(birth, m), c = new J.Chart(b, settings);
      const v = vimshottari(c.lon.Moon, c.utc.getTime(), c.settings.dasha_year);
      let score = 0; const detail = [];
      for (const ev of events) {
        if (!AREAS[ev.area]) continue;
        const when = Date.parse(String(ev.date).slice(0, 10) + "T00:00:00Z");
        const run = runningDasha(v, when);
        if (!run || isNaN(when)) continue;
        const sig = significators(c, AREAS[ev.area].houses), main = significators(c, [AREAS[ev.area].main]);
        const s = ["md", "ad", "pd"].reduce((a, k) => a + (main[run[k].lord] ? 2 : sig[run[k].lord] ? 1 : 0), 0);
        score += s;
        detail.push(`${ev.area} ${ev.date}: ${run.md.lord}/${run.ad.lord}/${run.pd.lord} -> ${s}`);
      }
      res.push({ offset_minutes: m, time: `${String(b.h).padStart(2, "0")}:${String(b.mi).padStart(2, "0")}`, lagna: SIGNS[c.lagna],
        d9_lagna: SIGNS[c.vargas[9].Lagna], score, detail });
    }
    return res.sort((a, b) => b.score - a.score || Math.abs(a.offset_minutes) - Math.abs(b.offset_minutes)).slice(0, 10);
  }

  // ---------------------------------------------------------------- dossier
  function buildDossier(birth, settings, nowMs = Date.now()) {
    const c = new J.Chart(birth, settings);
    const av = J.ashtakavarga(c.sign, c.lagna), shad = J.shadbala(c), comb = J.combustion(c), war = J.planetaryWar(c);
    const func = J.functionalNature(c), cond = J.planetCondition(c, comb, war, shad, func);
    const birthMs = c.utc.getTime();
    const v = vimshottari(c.lon.Moon, birthMs, c.settings.dasha_year), run = runningDasha(v, nowMs);
    const mdRows = v.mahadashas.map(md => ({ lord: md.lord, start: fmtDate(md.start), end: fmtDate(md.end),
      age_start: round(Math.floor((md.start - birthMs) / DAY) / 365.25, 1),
      antardashas: antardashas(md).map(a => ({ lord: a.lord, start: fmtDate(a.start), end: fmtDate(a.end) })) }));
    const current = run ? { mahadasha: run.md.lord, md_ends: fmtDate(run.md.end), antardasha: run.ad.lord, ad_ends: fmtDate(run.ad.end),
      pratyantar: run.pd.lord, pd_ends: fmtDate(run.pd.end) } : {};
    const winStart = birthMs + 365.25 * 16 * DAY, winEnd = nowMs + 365.25 * 30 * DAY, nowYm = fmtYm(nowMs);
    const ageAt = ym => { const [y, m] = ym.split("-").map(Number); return round(y + (m - 1) / 12 - (birth.y + (birth.mo - 1) / 12), 1); };
    const areas = {};
    const MIN_AGE = { father: 0, mother: 0, siblings: 0, health: 0, accidents_surgery: 0, mind: 0, love: 15, marriage: 18, children: 20, career: 18, govt_authority: 18, wealth: 18, property: 20, foreign: 17 };
    for (const area of Object.keys(AREAS)) {
      const st = birthMs + 365.25 * (MIN_AGE[area] ?? 16) * DAY;
      const pr = promise(c, area, av, cond), ew = eventWindows(c, area, st, winEnd);
      // always include the best windows of the next 15 years, even if far-off windows score higher
      const up = eventWindows(c, area, Math.max(nowMs, st), nowMs + 365.25 * 15 * DAY, 5);
      const key = w => w.start + w.md + w.ad;
      const have = new Set(ew.windows.map(key));
      for (const w of up.windows) if (!have.has(key(w))) ew.windows.push(w);
      ew.windows.sort((x, y) => (x.start < y.start ? -1 : 1));
      for (const w of ew.windows) { w.age_at_start = ageAt(w.start); w.is_past = w.end < nowYm; }
      const future = ew.windows.filter(w => !w.is_past);
      ew.next = future.find(w => !/^low/.test(w.confidence)) || future[0] || null;
      areas[area] = { promise: pr, timing: ew };
    }
    const vargas = {};
    for (const d of J.ALL_VARGAS) {
      const row = { meaning: J.VARGA_NAMES[d], Lagna: SIGNS[c.vargas[d].Lagna] };
      for (const p of PLANETS) row[p] = SIGNS[c.vargas[d][p]];
      vargas["D" + d] = row;
    }
    const jai = J.jaimini(c), ageNow = round(Math.floor((nowMs - birthMs) / DAY) / 365.25, 1), lg = jai.longevity;
    const upper = { "Short (Alpa)": 36, "Medium (Madhya)": 72, "Long (Purna)": 120 }[lg.category];
    lg.age_now = ageNow;
    if (ageNow > upper) lg.reality_check = `Native is already ${J.pyNum(ageNow)}, beyond the ${lg.category} range - this Jaimini indicator has not worked for this chart; do not lean on it.`;
    const mn = nakshatraOf(c.lon.Moon), el = Astro.norm(c.lon.Moon - c.lon.Sun);
    const pad = n => String(n).padStart(2, "0");
    return {
      input: { name: birth.name || "", local_time: `${birth.y}-${pad(birth.mo)}-${pad(birth.d)}T${pad(birth.h)}:${pad(birth.mi)}:${pad(birth.s || 0)}`,
        timezone: String(birth.tz), place: birth.place || "", lat: birth.lat, lon: birth.lon, gender: birth.gender || "",
        utc: c.utc.toISOString(), julian_day: round(c.jd, 6) },
      settings: { ayanamsa: c.settings.ayanamsa, node_type: c.settings.node_type, dasha_year: c.settings.dasha_year, chara_karaka_count: c.settings.chara_karaka_count },
      ayanamsa_value: round(c.snap.ayanamsa, 5), generated_for_date: fmtDate(nowMs),
      lagna: c.lagnaRow(),
      moon: { sign: SIGNS[c.moonSign], nakshatra: mn.name, pada: mn.pada, nakshatra_lord: mn.lord, gana: mn.gana, deity: mn.deity,
        paksha: el < 180 ? "Shukla (waxing)" : "Krishna (waning)", tithi: Math.floor(el / 12) + 1 },
      birth_day: { weekday_lord: c.sun.vara_lord, hora_lord: c.sun.hora_lord, day_birth: c.sun.is_day },
      planets: PLANETS.map(p => c.planetRow(p)), houses: c.houseRows(), bhava_chalit_shifts: c.bhavaChalit(), vargas,
      functional_nature: func, combustion: comb, planetary_war: war, gandanta: J.gandanta(c), planet_condition: cond, shadbala: shad,
      ashtakavarga: { bav_by_sign: Object.fromEntries(Object.entries(av.bav).map(([p, r]) => [p, Object.fromEntries(SIGNS.map((s, i) => [s, r[i]]))])),
        sav_by_house: J.interpretSav(av.sav, c.lagna) },
      yogas: J.yogas(c, comb, war, shad), doshas: J.doshas(c), jaimini: jai,
      vimshottari: { birth_dasha_lord: v.birth_lord, balance_at_birth_years: v.balance_years, year_length_days: v.year_days, current, mahadashas: mdRows },
      transits_now: transitReport(c, nowMs, av), saturn_cycles: sadeSatiPeriods(c, birthMs, 100),
      life_areas: areas, profiles: J.profiles(c),
      health_vigilance_periods: marakaPeriods(c, birthMs + 365.25 * 18 * DAY, birthMs + 365.25 * 100 * DAY),
      remedies: { gemstones: J.gemAdvice(c, func, cond, shad, comb), mantra_daan: J.mantraDaan(c, func, cond), lal_kitab: J.lalKitab(c) },
      birth_time_sensitivity: sensitivity(birth, settings, 30),
      variants_in_use: Object.fromEntries(Object.entries(J.VARIANTS).map(([k, x]) => [k, { choice: c.settings[k], note: x.note }])),
    };
  }

  Object.assign(J, { GOCHAR, AREAS, transitReport, sadeSatiPeriods, significators, promise, eventWindows, marakaPeriods,
    sensitivity, rectifyByEvents, buildDossier, shiftBirth });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
