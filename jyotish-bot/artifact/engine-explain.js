/* Plain-language layer: turns every technical factor into "what this means for your life".
   Adds `plain` fields to the dossier built by engine-time.js. */
(function (root) {
  const J = root.J || require("./engine-time.js");
  const { SIGN_LORD, houseFrom } = J;

  const HOUSE = {
    1: "your body, health, looks and confidence", 2: "money savings, family life and the way you speak",
    3: "courage, your own efforts, siblings and short trips", 4: "home, mother, property, vehicles and peace of mind",
    5: "studies, intelligence, children, love life and creativity", 6: "job/service, competition, loans, illness and enemies",
    7: "marriage, spouse and business partners", 8: "sudden events, in-laws' money, secrets, surgery and long-term health",
    9: "luck, father, teachers, religion and long journeys", 10: "career, work, reputation and status",
    11: "income, profits, friends and wishes coming true", 12: "expenses, foreign lands, sleep, isolation and spiritual life",
  };
  const SHORT = { 1: "self & health", 2: "money & family", 3: "courage & siblings", 4: "home & mother", 5: "studies, children & love",
    6: "job, loans & illness", 7: "marriage & partners", 8: "sudden events & hidden matters", 9: "luck & father", 10: "career & status",
    11: "income & gains", 12: "expenses & foreign" };
  const PLANET = {
    Sun: "confidence, father, government and authority", Moon: "mind, emotions, mother and public image",
    Mars: "energy, courage, property, brothers and anger", Mercury: "communication, studies, business and quick thinking",
    Jupiter: "wisdom, money growth, children, teachers and (for women) husband", Venus: "love, marriage, comforts, beauty, vehicles and art",
    Saturn: "hard work, discipline, delays, servants and long-term results", Rahu: "ambition, foreign things, technology, sudden and unusual events",
    Ketu: "detachment, spirituality, research and sudden breaks",
  };
  const MALEFIC_EFFECT = {
    Sun: "ego clashes and a dominating attitude", Mars: "arguments, anger or heat in the relationship/area",
    Saturn: "delays, seriousness, heavy responsibility (results come late but last)", Rahu: "confusion, unusual or unconventional situations, restlessness",
    Ketu: "dissatisfaction, distance or detachment", Moon: "emotional ups and downs", Mercury: "mixed results",
  };
  const BENEFIC_EFFECT = {
    Jupiter: "protection, wisdom and growth", Venus: "harmony, love and comfort", Mercury: "good communication and smart choices",
    Moon: "care and emotional support",
  };
  const DIG_PLAIN = {
    Exalted: "at its strongest", Moolatrikona: "very strong", Own: "strong (in its own home)", "Great Friend": "comfortable",
    Friend: "fairly comfortable", Neutral: "average", Enemy: "uncomfortable", "Great Enemy": "very uncomfortable",
    Debilitated: "at its weakest",
  };
  const AREA_EVENT = {
    marriage: "a good time for marriage, engagement or a serious relationship to start",
    career: "a job change, promotion, new job or a big career move", wealth: "income rise, savings or a financial gain",
    children: "childbirth or good news about children", education: "admission, exam success or completing a degree",
    property: "buying a house, land or vehicle", foreign: "foreign travel, a move abroad or work linked to foreign places",
    health: "health needs care - illness, a hospital visit or a check-up finding something is possible",
    father: "important events for your father (career, health or family matters)", mother: "important events for your mother or home",
    siblings: "events involving brothers/sisters", mind: "a phase that strongly affects your mood and peace of mind",
    govt_authority: "a government job, authority, award or public recognition",
    accidents_surgery: "risk of an accident, injury or surgery - drive carefully and avoid risks",
    spirituality: "spiritual growth, pilgrimage or a strong interest in meditation/religion",
    litigation: "disputes, debts or conflicts - avoid lending money and legal fights",
  };
  const DURATION = { Sun: "about a month", Moon: "2-3 days", Mars: "about 6 weeks", Mercury: "3-4 weeks", Jupiter: "about a year",
    Venus: "about a month", Saturn: "about 2.5 years", Rahu: "about 1.5 years", Ketu: "about 1.5 years" };
  const GOCHAR_GOOD = { 1: "fresh energy and recognition", 2: "money comes in and family is happy", 3: "courage, success through effort, wins over rivals",
    4: "comfort at home, gains in property or vehicles", 5: "good ideas, happiness from children or love", 6: "victory over rivals, health improves, debts reduce",
    7: "good for spouse, partnerships and travel", 8: "unexpected gains", 9: "luck helps you, blessings, good travel",
    10: "career success and status", 11: "income and gains, wishes fulfilled", 12: "money spent on good things, peaceful sleep" };
  const GOCHAR_BAD = { 1: "tiredness, stress or health trouble", 2: "expenses, family friction, harsh words", 3: "low courage, trouble with siblings",
    4: "unrest at home, mother's health or vehicle trouble", 5: "worry about studies/children, poor decisions", 6: "illness, enemies or debts trouble you",
    7: "friction with spouse or partners, travel trouble", 8: "obstacles, health scares, sudden setbacks", 9: "bad luck, friction with father or teachers",
    10: "work pressure and problems at the job", 11: "gains get delayed", 12: "expenses, losses, poor sleep" };

  const isBen = p => ["Jupiter", "Venus", "Mercury", "Moon"].includes(p);
  const list = a => a.length <= 1 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];

  // ---------------------------------------------------------------- one factor -> plain sentence
  function plainFactor(t, area) {
    let m;
    if ((m = t.match(/^(\w+) occupies house (\d+)$/))) {
      const [, p, h] = m;
      return isBen(p) ? `${p} sits in this area: brings ${BENEFIC_EFFECT[p] || "support"} to ${HOUSE[h]}.`
        : `${p} sits in this area: expect ${MALEFIC_EFFECT[p] || "pressure"} in matters of ${HOUSE[h]}.`;
    }
    if ((m = t.match(/^(\w+) aspects house (\d+)$/))) {
      const [, p, h] = m;
      return isBen(p) ? `${p} looks at this area: adds ${BENEFIC_EFFECT[p] || "support"}.`
        : `${p} looks at this area: adds ${MALEFIC_EFFECT[p] || "pressure"}.`;
    }
    if ((m = t.match(/^house lord (\w+) is ([\w ]+) in house (\d+)$/))) {
      const [, p, d, h] = m;
      return `${p}, the planet in charge of this area, is ${DIG_PLAIN[d] || d.toLowerCase()} and sits in your house of ${SHORT[h]} - so this area gets tied to ${HOUSE[h]}.`;
    }
    if ((m = t.match(/^house lord (\w+) sits in dusthana (\d+)$/))) return `Its ruling planet ${m[1]} sits in a difficult house (${SHORT[m[2]]}) - expect struggle, delay or worry here.`;
    if ((m = t.match(/^house lord (\w+) in kendra\/trikona$/))) return `Its ruling planet ${m[1]} is well placed - this area gets steady support.`;
    if ((m = t.match(/^karaka (\w+): (\d+) strengths vs (\d+) weaknesses$/))) {
      const [, p, s, w] = m, net = +s - +w;
      return `${p}, the natural sign-giver for this area, is ${net >= 2 ? "strong" : net >= 0 ? "okay" : "weak"} overall (${s} good points, ${w} bad).`;
    }
    if ((m = t.match(/^SAV bindus in house (\d+): (\d+) \((good|weak)\)$/))) return m[3] === "good"
      ? `This house scores high (${m[2]} points) - results here come more easily.` : `This house scores low (${m[2]} points) - results here need extra effort.`;
    if ((m = t.match(/^in D(\d+), house lord (\w+) is in \w+ \(([\w ]+)\)$/))) return `In the detailed chart for this area (D${m[1]}), the ruler is ${DIG_PLAIN[m[3]] || m[3].toLowerCase()} - ${(J.DIGNITY_SCORE[m[3]] ?? 0) > 0 ? "the deeper promise holds up" : "the deeper promise is weaker than it looks"}.`;
    if ((m = t.match(/^in D(\d+), house lord falls in house (\d+) from D\d+ lagna$/))) return [6, 8, 12].includes(+m[2])
      ? `In the detailed chart (D${m[1]}) the ruler falls in a difficult house - hidden problems or delays.` : `In the detailed chart (D${m[1]}) the ruler is well placed.`;
    if ((m = t.match(/^in D(\d+), karaka (\w+) is ([\w ]+)$/))) return `In the detailed chart (D${m[1]}), ${m[2]} is ${DIG_PLAIN[m[3]] || m[3].toLowerCase()}.`;
    if ((m = t.match(/^malefics \[(.+)\] in house (\d+) from Moon$/))) return `Seen from your Moon (your mind), ${m[1].replace(/'/g, "")} press on this area - it can feel emotionally stressful.`;
    return t;
  }

  const VERDICT = {
    strong: "Strong. The chart clearly supports this area; it is likely to go well.",
    moderate: "Mixed. It happens, but with some effort, delay or compromise.",
    weak: "Weak. Expect obstacles here - delays, struggle or dissatisfaction.",
    "very weak": "Very weak. A difficult area in your chart - serious problems are likely, or it may not happen the way you hope.",
  };
  function plainVerdict(v) {
    if (/protection/.test(v)) {
      if (/vulnerable/.test(v)) return "Sensitive area. You are vulnerable here - be careful and act early (check-ups, caution, no risks).";
      return v.startsWith("strong") ? "Well protected. Problems in this area stay limited." : "Average protection. Some trouble is possible but manageable.";
    }
    return VERDICT[v] || v;
  }

  // ---------------------------------------------------------------- dasha meaning
  function periodTone(D, p) {
    const f = D.functional_nature.planets[p], c = D.planet_condition[p];
    const benefic = /^(Benefic|Yogakaraka)/.test(f.verdict) || (/dispositor/.test(f.verdict) && /^(Benefic|Yogakaraka)/.test(f.dispositor_verdict || ""));
    const malefic = /^Malefic/.test(f.verdict) || /^Malefic/.test(f.dispositor_verdict || "");
    if (benefic && c.net >= 1) return ["good", "mostly good - growth and support"];
    if (benefic) return ["mixed", "good intentions but weak delivery - results come with effort"];
    if (malefic && c.net < 0) return ["hard", "testing - struggles and pressure; work hard and be careful"];
    if (malefic) return ["mixed", "mixed - gains come with stress or a price"];
    return ["mixed", "mixed - depends on what you do"];
  }
  function periodTopics(D, p) {
    const row = D.planets.find(x => x.planet === p);
    const hs = [row.house, ...row.owns_houses].filter((h, i, a) => a.indexOf(h) === i);
    return hs.map(h => SHORT[h]);
  }
  function mdPlain(D, p) {
    const [tone, t] = periodTone(D, p);
    return { tone, text: `${p} period: life focuses on ${list(periodTopics(D, p))}. Themes of ${PLANET[p]}. Overall ${t}.` };
  }
  function adPlain(D, md, ad) {
    const [tone, t] = periodTone(D, ad);
    const sm = J.SIGNS.indexOf(D.planets.find(x => x.planet === md).sign), sa = J.SIGNS.indexOf(D.planets.find(x => x.planet === ad).sign);
    const rel = houseFrom(sm, sa);
    let extra = "";
    if ([6, 8, 12].includes(rel) && md !== ad) extra = ` ${ad} sits ${rel}th from ${md}, so the two pull in different directions - friction, delays or health strain.`;
    else if ([1, 5, 9].includes(rel)) extra = ` ${ad} and ${md} work well together, so results flow smoothly.`;
    return { tone, text: `${list(periodTopics(D, ad))} come into focus - ${t}.${extra}` };
  }

  // ---------------------------------------------------------------- build
  function explain(D) {
    const plain = {};
    // life areas
    for (const [k, a] of Object.entries(D.life_areas)) {
      const p = a.promise;
      p.plain = plainVerdict(p.verdict);
      p.favourable_plain = p.favourable.map(t => plainFactor(t, k));
      p.unfavourable_plain = p.unfavourable.map(t => plainFactor(t, k));
      for (const w of a.timing.windows) {
        const sure = /high/.test(w.confidence) ? "Strong chance: both your dasha and the slow planets (Jupiter + Saturn) point to it."
          : /medium/.test(w.confidence) ? "Possible: some signs point to it, not all." : "Weak chance: only the dasha points to it.";
        w.plain = `${AREA_EVENT[k][0].toUpperCase() + AREA_EVENT[k].slice(1)}, most likely around ${w.peak} (during ${w.md}/${w.ad}). ${sure}${w.is_past ? " This is in the past - did something like this happen? If yes, the chart's timing is working for you." : ""}`;
      }
    }
    // dashas
    for (const md of D.vimshottari.mahadashas) {
      Object.assign(md, { plain: mdPlain(D, md.lord) });
      for (const ad of md.antardashas) ad.plain = adPlain(D, md.lord, ad.lord);
    }
    const cur = D.vimshottari.current;
    if (cur.mahadasha) {
      const md = mdPlain(D, cur.mahadasha), ad = adPlain(D, cur.mahadasha, cur.antardasha);
      plain.now = `You are in ${cur.mahadasha} mahadasha (till ${cur.md_ends}) and ${cur.antardasha} antardasha (till ${cur.ad_ends}). ${md.text} Right now: ${ad.text}`;
    }
    // strength
    plain.strength = {};
    for (const [p, s] of Object.entries(D.shadbala.planets)) {
      const owns = D.planets.find(x => x.planet === p).owns_houses.map(h => SHORT[h]);
      const lvl = s.ratio >= 1.3 ? "strong" : s.ratio >= 1 ? "strong enough" : s.ratio >= 0.9 ? "slightly weak" : "weak";
      const effect = s.ratio >= 1 ? "work well and give results without much struggle" : "need extra effort; results come late or only partly";
      s.plain = `${p} is ${lvl}. What this means for you: ${PLANET[p]}, and the parts of life ${p} runs in your chart (${list(owns)}), ${effect}.`;
      plain.strength[p] = s.plain;
    }
    for (const h of D.ashtakavarga.sav_by_house) h.plain = `${SHORT[h.house]}: ${h.quality === "weak" ? "needs extra effort" : h.quality === "average" ? "average" : "comes easily"}`;
    // transits
    for (const r of D.transits_now.planets) {
      const h = r.house_from_moon, good = /^favourable/.test(r.verdict);
      let t = good ? `Good for you now: ${GOCHAR_GOOD[h]}.` : `Not easy now: ${GOCHAR_BAD[h]}.`;
      if (r.vedha_by.length) t += ` But ${list(r.vedha_by)} blocks it, so the good effect is reduced.`;
      if (r.planet in { Sun: 1, Moon: 1, Mars: 1, Mercury: 1, Jupiter: 1, Venus: 1, Saturn: 1 }) {
        const b = +((r.verdict.match(/(\d+) bindus/) || [])[1]);
        if (!isNaN(b)) t += good ? (b >= 4 ? " Your chart supports it well, so you feel the good clearly." : " Your chart gives it little support, so the good stays small.")
          : (b >= 4 ? " Your chart supports this planet, so the trouble stays mild." : " Your chart gives it little support, so you may feel it more.");
      }
      r.plain = `${t} Lasts ${DURATION[r.planet]}.`;
    }
    const tn = D.transits_now;
    plain.saturn = tn.sade_sati_or_dhaiya ? `${tn.sade_sati_or_dhaiya}. ` : "Saturn is not pressuring your Moon right now - no Sade Sati or Dhaiya. ";
    // yogas and doshas
    for (const y of D.yogas) {
      if (y.category === "Debility") { y.plain = /NOT/.test(y.verdict) ? `${y.planets[0]} stays weak - its areas (${list(periodTopics(D, y.planets[0]))}) need effort.` : `${y.planets[0]} starts weak but recovers - early struggle, later rise in ${list(periodTopics(D, y.planets[0]))}.`; continue; }
      y.plain = y.verdict === "active" ? `You get this: ${y.result}.` : y.verdict === "weakened" ? `You get this only partly: ${y.result}.` : `Cancelled - don't expect: ${y.result}.`;
    }
    for (const d of D.doshas) d.plain = !d.present ? "You don't have this." : d.cancellations.length ? `Present but reduced: ${d.effect} - milder than usual.` : `Present: ${d.effect}.`;
    // summary
    const ranked = Object.entries(D.life_areas).filter(([k]) => !["health", "litigation", "accidents_surgery"].includes(k))
      .map(([k, a]) => [k, a.promise]).sort((x, y) => y[1].score - x[1].score);
    plain.best = ranked.slice(0, 3).map(([, p]) => `${p.area} (${p.verdict})`);
    plain.worst = ranked.slice(-3).reverse().map(([, p]) => `${p.area} (${p.verdict})`);
    const h = D.life_areas.health.promise;
    plain.health = plainVerdict(h.verdict);
    const active = D.yogas.filter(y => y.verdict === "active" && !["Nabhasa", "Debility"].includes(y.category)).map(y => y.name);
    plain.yogas = active.length ? `Working yogas: ${list(active.slice(0, 5))}.` : "No major yoga works fully; the strong ones are weakened or cancelled.";
    const doshas = D.doshas.filter(d => d.present && !d.cancellations.length).map(d => d.name);
    plain.doshas = doshas.length ? `Doshas that are fully active: ${list(doshas)}.` : "No dosha is fully active (any present are reduced by cancellations).";
    D.plain = plain;
    return D;
  }

  Object.assign(J, { explain, plainFactor, HOUSE_PLAIN: HOUSE });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
