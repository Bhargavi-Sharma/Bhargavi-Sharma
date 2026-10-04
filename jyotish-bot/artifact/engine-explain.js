/* Plain-language layer: turns every technical factor into "what this means for your life".
   Adds `plain` fields to the dossier built by engine-time.js, in the chosen language (see lang.js). */
(function (root) {
  const J = root.J || require("./engine-time.js");
  if (!J.LANG && typeof require !== "undefined") require("./lang.js");
  const { houseFrom } = J;
  const isBen = p => ["Jupiter", "Venus", "Mercury", "Moon"].includes(p);

  function plainFactor(t, L) {
    L = L || J.LANG.en;
    const P = L.planet, T = L.t;
    let m;
    if ((m = t.match(/^(\w+) occupies house (\d+)$/))) {
      const [, p, h] = m;
      return isBen(p) ? T.occBen(P(p), L.BEN[p] || L.BEN.Jupiter, L.HOUSE[h]) : T.occMal(P(p), L.MAL[p] || L.MAL.Mercury, L.HOUSE[h]);
    }
    if ((m = t.match(/^(\w+) aspects house (\d+)$/))) {
      const [, p] = m;
      return isBen(p) ? T.aspBen(P(p), L.BEN[p] || L.BEN.Jupiter) : T.aspMal(P(p), L.MAL[p] || L.MAL.Mercury);
    }
    if ((m = t.match(/^house lord (\w+) is ([\w ]+) in house (\d+)$/))) return T.lord(P(m[1]), L.DIG[m[2]] || m[2], L.SHORT[m[3]], L.HOUSE[m[3]]);
    if ((m = t.match(/^house lord (\w+) sits in dusthana (\d+)$/))) return T.lordDus(P(m[1]), L.SHORT[m[2]]);
    if ((m = t.match(/^house lord (\w+) in kendra\/trikona$/))) return T.lordGood(P(m[1]));
    if ((m = t.match(/^karaka (\w+): (\d+) strengths vs (\d+) weaknesses$/))) {
      const net = +m[2] - +m[3];
      return T.karaka(P(m[1]), net >= 2 ? T.lvl.strong : net >= 0 ? T.lvl.ok : T.lvl.weak, m[2], m[3]);
    }
    if ((m = t.match(/^SAV bindus in house (\d+): (\d+) \((good|weak)\)$/))) return m[3] === "good" ? T.savGood(m[2]) : T.savWeak(m[2]);
    if ((m = t.match(/^in D(\d+), house lord (\w+) is in \w+ \(([\w ]+)\)$/))) return T.vargaLord(m[1], L.DIG[m[3]] || m[3], (J.DIGNITY_SCORE[m[3]] ?? 0) > 0);
    if ((m = t.match(/^in D(\d+), house lord falls in house (\d+) from D\d+ lagna$/))) return [6, 8, 12].includes(+m[2]) ? T.vargaHouseBad(m[1]) : T.vargaHouseGood(m[1]);
    if ((m = t.match(/^in D(\d+), karaka (\w+) is ([\w ]+)$/))) return T.vargaKar(m[1], P(m[2]), L.DIG[m[3]] || m[3]);
    if ((m = t.match(/^malefics \[(.+)\] in house (\d+) from Moon$/))) return T.moonMal(L.list(m[1].replace(/'/g, "").split(", ").map(P)));
    return t;
  }

  function plainVerdict(v, L) {
    if (/protection/.test(v)) return /vulnerable/.test(v) ? L.VERDICT.vulnerable : v.startsWith("strong") ? L.VERDICT.protected : L.VERDICT.avgprot;
    return L.VERDICT[v] || v;
  }
  function periodTone(D, p) {
    const f = D.functional_nature.planets[p], c = D.planet_condition[p];
    const benefic = /^(Benefic|Yogakaraka)/.test(f.verdict) || (/dispositor/.test(f.verdict) && /^(Benefic|Yogakaraka)/.test(f.dispositor_verdict || ""));
    const malefic = /^Malefic/.test(f.verdict) || /^Malefic/.test(f.dispositor_verdict || "");
    if (benefic && c.net >= 1) return ["good", "good"];
    if (benefic) return ["mixed", "benweak"];
    if (malefic && c.net < 0) return ["hard", "hard"];
    if (malefic) return ["mixed", "malmixed"];
    return ["mixed", "mixed"];
  }
  function periodTopics(D, p, L) {
    const row = D.planets.find(x => x.planet === p);
    return [row.house, ...row.owns_houses].filter((h, i, a) => a.indexOf(h) === i).map(h => L.SHORT[h]);
  }
  function mdPlain(D, p, L) {
    const [tone, key] = periodTone(D, p);
    return { tone, tone_label: L.TONEWORD[tone], text: L.t.md(L.planet(p), L.list(periodTopics(D, p, L)), L.PLANET[p], L.TONE[key]) };
  }
  function adPlain(D, md, ad, L) {
    const [tone, key] = periodTone(D, ad);
    const sm = J.SIGNS.indexOf(D.planets.find(x => x.planet === md).sign), sa = J.SIGNS.indexOf(D.planets.find(x => x.planet === ad).sign);
    const rel = houseFrom(sm, sa);
    let extra = "";
    if ([6, 8, 12].includes(rel) && md !== ad) extra = L.t.adBad(L.planet(ad), rel, L.planet(md));
    else if ([1, 5, 9].includes(rel)) extra = L.t.adGood(L.planet(ad), L.planet(md));
    return { tone, tone_label: L.TONEWORD[tone], text: L.t.ad(L.list(periodTopics(D, ad, L)), L.TONE[key], extra) };
  }

  function explain(D, lang = "en") {
    const L = J.LANG[lang] || J.LANG.en, T = L.t, P = L.planet, plain = { lang };
    for (const [k, a] of Object.entries(D.life_areas)) {
      const p = a.promise;
      p.area_label = L.AREA[k] || p.area;
      p.verdict_label = /protection/.test(p.verdict) ? p.verdict : (L.VWORD[p.verdict] || p.verdict);
      p.plain = plainVerdict(p.verdict, L);
      p.favourable_plain = p.favourable.map(t => plainFactor(t, L));
      p.unfavourable_plain = p.unfavourable.map(t => plainFactor(t, L));
      for (const w of a.timing.windows) {
        const sure = /high/.test(w.confidence) ? T.sureHigh : /medium/.test(w.confidence) ? T.sureMed : T.sureLow;
        w.plain = T.win(L.EVENT[k], w.peak, P(w.md), P(w.ad), sure, w.is_past);
      }
    }
    for (const md of D.vimshottari.mahadashas) {
      md.plain = mdPlain(D, md.lord, L);
      for (const ad of md.antardashas) ad.plain = adPlain(D, md.lord, ad.lord, L);
    }
    const cur = D.vimshottari.current;
    if (cur.mahadasha) plain.now = T.now(P(cur.mahadasha), cur.md_ends, P(cur.antardasha), cur.ad_ends, mdPlain(D, cur.mahadasha, L).text, adPlain(D, cur.mahadasha, cur.antardasha, L).text);
    plain.strength = {};
    for (const [p, s] of Object.entries(D.shadbala.planets)) {
      const owns = D.planets.find(x => x.planet === p).owns_houses.map(h => L.SHORT[h]);
      const lvl = s.ratio >= 1.3 ? T.strLvl.strong : s.ratio >= 1 ? T.strLvl.enough : s.ratio >= 0.9 ? T.strLvl.slight : T.strLvl.weak;
      s.plain = T.str(P(p), lvl, L.PLANET[p], L.list(owns), s.ratio >= 1);
      plain.strength[p] = s.plain;
    }
    for (const h of D.ashtakavarga.sav_by_house) h.plain = `${L.SHORT[h.house]}: ${T.sav[h.quality === "weak" ? "weak" : h.quality === "average" ? "average" : "good"]}`;
    for (const r of D.transits_now.planets) {
      const h = r.house_from_moon, good = /^favourable/.test(r.verdict);
      let t = good ? T.trGood(L.GOOD[h]) : T.trBad(L.BAD[h]);
      if (r.vedha_by.length) t += T.vedha(L.list(r.vedha_by.map(P)));
      if (J.SEVEN.includes(r.planet)) {
        const b = +((r.verdict.match(/(\d+) bindus/) || [])[1]);
        if (!isNaN(b)) t += good ? (b >= 4 ? T.bGoodHi : T.bGoodLo) : (b >= 4 ? T.bBadHi : T.bBadLo);
      }
      r.plain = t + T.lasts(L.DUR[r.planet]);
    }
    const tn = D.transits_now;
    plain.saturn = tn.sade_sati_or_dhaiya ? `${T.sade[tn.saturn_from_moon] || tn.sade_sati_or_dhaiya}. ` : T.satNone;
    const res = r => L.RESULT[r] || L.RESULT[String(r).split(" (")[0]] || r;
    for (const y of D.yogas) {
      if (y.category === "Debility") { const a = L.list(periodTopics(D, y.planets[0], L)); y.plain = /NOT/.test(y.verdict) ? T.debNo(P(y.planets[0]), a) : T.debYes(P(y.planets[0]), a); continue; }
      y.plain = y.verdict === "active" ? T.yActive(res(y.result)) : y.verdict === "weakened" ? T.yWeak(res(y.result)) : T.yCanc(res(y.result));
    }
    for (const d of D.doshas) d.plain = !d.present ? T.dNo : d.cancellations.length ? T.dReduced(res(d.effect)) : T.dYes(res(d.effect));
    const ranked = Object.entries(D.life_areas).filter(([k]) => !["health", "litigation", "accidents_surgery"].includes(k))
      .map(([k, a]) => [k, a.promise]).sort((x, y) => y[1].score - x[1].score);
    plain.best = ranked.slice(0, 3).map(([, p]) => `${p.area_label} (${p.verdict_label})`);
    plain.worst = ranked.slice(-3).reverse().map(([, p]) => `${p.area_label} (${p.verdict_label})`);
    plain.health = plainVerdict(D.life_areas.health.promise.verdict, L);
    const active = D.yogas.filter(y => y.verdict === "active" && !["Nabhasa", "Debility"].includes(y.category)).map(y => y.name);
    plain.yogas = active.length ? T.yogas(L.list(active.slice(0, 5))) : T.noYogas;
    const ds = D.doshas.filter(d => d.present && !d.cancellations.length).map(d => d.name);
    plain.doshas = ds.length ? T.doshas(L.list(ds)) : T.noDoshas;
    D.plain = plain;
    return D;
  }

  Object.assign(J, { explain, plainFactor });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
