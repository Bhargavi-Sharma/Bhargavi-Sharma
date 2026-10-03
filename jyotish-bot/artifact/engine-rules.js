/* Yogas, doshas, Jaimini, profiles and remedies (port of yogas.py, doshas.py, jaimini.py, profiles.py, remedies.py). */
(function (root) {
  const J = root.J || require("./engine-core.js");
  const { PLANETS, SEVEN, SIGNS, SIGN_LORD, MODALITY, OWN_SIGNS, EXALTATION, NATURAL_FRIENDS, GANDMOOL, houseFrom, pyList,
    exaltSign, dignity, baladiAvastha, nakshatraOf, round, pyNum } = J;
  const pyNums = a => "[" + a.join(", ") + "]";
  const BENEFICS = ["Jupiter", "Venus", "Mercury"];
  const MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"];

  // ---------------------------------------------------------------- yogas
  const Y_ = (name, category, planets, conditions, cancellations, source, result, weakenings = []) => ({
    name, category, planets, conditions, cancellations, weakenings,
    verdict: cancellations.length ? "cancelled" : weakenings.length ? "weakened" : "active", source, result });
  function afflictions(c, p, comb, losers) {
    const w = [];
    if (comb[p]) w.push(`${p} combust`);
    if (losers.has(p)) w.push(`${p} lost planetary war`);
    if (c.dig[p] === "Debilitated") w.push(`${p} debilitated`);
    if ([6, 8, 12].includes(c.house[p])) w.push(`${p} in dusthana ${c.house[p]}`);
    const nodes = c.conjunct(p).filter(q => q === "Rahu" || q === "Ketu");
    if (nodes.length && p !== "Rahu" && p !== "Ketu") w.push(`${p} conjunct ${nodes[0]} (eclipsed/obsessive quality)`);
    return w;
  }
  const kendraFrom = (c, p, ref) => [1, 4, 7, 10].includes(houseFrom(ref, c.sign[p]));

  function yogas(c, comb, war, shad) {
    const Y = [], losers = new Set(war.map(w => w.loser)), L = c.lagna, M = c.moonSign;
    const names = { Mars: "Ruchaka", Mercury: "Bhadra", Jupiter: "Hamsa", Venus: "Malavya", Saturn: "Shasha" };
    const results = { Ruchaka: "courage, command, land, martial success", Bhadra: "intellect, eloquence, business skill",
      Hamsa: "wisdom, righteousness, respect", Malavya: "luxury, beauty, spouse, vehicles, arts",
      Shasha: "authority over many, organisational power, wealth via labour/masses" };
    for (const [p, n] of Object.entries(names)) {
      const strong = OWN_SIGNS[p].includes(c.sign[p]) || c.sign[p] === EXALTATION[p][0];
      if (strong && [1, 4, 7, 10].includes(c.house[p])) {
        const weak = afflictions(c, p, comb, losers);
        if (c.conjunct(p).some(q => q === "Sun" || q === "Moon"))
          weak.push(`${p} conjunct Sun/Moon - some commentators on Phaladeepika say results come only in its own dasha`);
        if (shad.planets[p].ratio < 1) weak.push(`${p} shadbala below required (${pyNum(shad.planets[p].ratio)}x)`);
        Y.push(Y_(`${n} (Pancha Mahapurusha)`, "Mahapurusha", [p], [`${p} in ${SIGNS[c.sign[p]]} (${c.dig[p]}) in kendra ${c.house[p]} from lagna`],
          [], "BPHS ch.75; Phaladeepika ch.6", results[n], weak));
      } else if (strong && kendraFrom(c, p, M)) {
        Y.push(Y_(`${n} from Moon (secondary)`, "Mahapurusha", [p], [`${p} own/exalted in kendra from Moon (not from lagna)`], [],
          "Some authors count from Moon too; BPHS counts from lagna", results[n], ["formed from Moon only - weaker than from lagna"]));
      }
    }
    const el = J.Astro.norm(c.lon.Moon - c.lon.Sun);
    if ([1, 4, 7, 10].includes(houseFrom(M, c.sign.Jupiter))) {
      const weak = afflictions(c, "Jupiter", comb, losers);
      if (c.dig.Moon === "Debilitated") weak.push("Moon debilitated");
      if (el < 72 || el > 288) weak.push("Moon dark (near new moon) - weak Moon");
      Y.push(Y_("Gajakesari", "Lunar", ["Jupiter", "Moon"], [`Jupiter in house ${houseFrom(M, c.sign.Jupiter)} from Moon`], [],
        "BPHS ch.36; Phaladeepika ch.6; Jataka Parijata", "fame, intelligence, lasting reputation, victory over rivals", weak));
    }
    const excl = ["Sun", "Rahu", "Ketu", "Moon"];
    const second = PLANETS.filter(p => !excl.includes(p) && houseFrom(M, c.sign[p]) === 2);
    const twelfth = PLANETS.filter(p => !excl.includes(p) && houseFrom(M, c.sign[p]) === 12);
    if (second.length && twelfth.length)
      Y.push(Y_("Durudhara", "Lunar", second.concat(twelfth), [`${pyList(second)} in 2nd and ${pyList(twelfth)} in 12th from Moon`], [],
        "Brihat Jataka ch.13; BPHS ch.37", "wealth, vehicles, generosity, comforts"));
    else if (second.length)
      Y.push(Y_("Sunapha", "Lunar", second, [`${pyList(second)} in 2nd from Moon`], [], "Brihat Jataka ch.13; BPHS ch.37",
        "self-earned wealth, good intellect and reputation"));
    else if (twelfth.length)
      Y.push(Y_("Anapha", "Lunar", twelfth, [`${pyList(twelfth)} in 12th from Moon`], [], "Brihat Jataka ch.13; BPHS ch.37",
        "good health, pleasing personality, renunciation late in life"));
    else {
      const canc = [];
      const kl = SEVEN.filter(p => p !== "Moon" && [1, 4, 7, 10].includes(c.house[p]));
      const km = SEVEN.filter(p => p !== "Moon" && [4, 7, 10].includes(houseFrom(M, c.sign[p])));
      if (kl.length) canc.push(`planets in kendra from lagna: ${pyList(kl)} (BPHS ch.37; Phaladeepika ch.6)`);
      if (km.length) canc.push(`planets in kendra from Moon: ${pyList(km)} (Phaladeepika ch.6)`);
      if (c.planetAspectedBy("Moon").includes("Jupiter")) canc.push("Jupiter aspects the Moon");
      if (c.conjunct("Moon").length) canc.push(`Moon conjunct ${pyList(c.conjunct("Moon"))} (Saravali)`);
      Y.push(Y_("Kemadruma", "Lunar (dosha)", ["Moon"], ["no planet (except Sun/nodes) in 2nd or 12th from Moon"], canc,
        "Brihat Jataka ch.13; BPHS ch.37; Phaladeepika ch.6 (cancellations)", "poverty, sorrow, dependence, mental unrest - if not cancelled"));
    }
    const S = c.sign.Sun, ex = ["Moon", "Rahu", "Ketu", "Sun"];
    const v2 = PLANETS.filter(p => !ex.includes(p) && houseFrom(S, c.sign[p]) === 2);
    const v12 = PLANETS.filter(p => !ex.includes(p) && houseFrom(S, c.sign[p]) === 12);
    if (v2.length && v12.length) Y.push(Y_("Ubhayachari", "Solar", v2.concat(v12), [`${pyList(v2)} 2nd and ${pyList(v12)} 12th from Sun`], [], "BPHS ch.38", "king-like, eloquent, balanced, prosperous"));
    else if (v2.length) Y.push(Y_("Vesi", "Solar", v2, [`${pyList(v2)} in 2nd from Sun`], [], "BPHS ch.38", "truthful, balanced; results follow the nature of the planet (benefic good, malefic mixed)"));
    else if (v12.length) Y.push(Y_("Vasi", "Solar", v12, [`${pyList(v12)} in 12th from Sun`], [], "BPHS ch.38", "skilful, charitable, happy; results follow the planet's nature"));
    if (c.sign.Mercury === c.sign.Sun) {
      const w = comb.Mercury && comb.Mercury.deep ? [`Mercury deeply combust (${pyNum(comb.Mercury.distance_from_sun)}°)`] : [];
      Y.push(Y_("Budhaditya", "Combination", ["Sun", "Mercury"], ["Sun and Mercury in the same sign"], [],
        "Popular (derived from BPHS/Saravali Sun-Mercury conjunction results)", "intelligence, skill, good reputation", w));
    }
    if (c.sign.Moon === c.sign.Mars || houseFrom(c.sign.Moon, c.sign.Mars) === 7)
      Y.push(Y_("Chandra-Mangala", "Combination", ["Moon", "Mars"], ["Moon and Mars conjunct or opposite"], [], "Phaladeepika ch.6",
        "earning through trade/enterprise; can indicate harshness to mother"));
    const adhi = BENEFICS.filter(p => [6, 7, 8].includes(houseFrom(M, c.sign[p])));
    if (adhi.length) {
      let weak = adhi.length === 3 ? [] : [`only ${adhi.length}/3 benefics - partial Adhi yoga`];
      for (const p of adhi) weak = weak.concat(afflictions(c, p, comb, losers));
      Y.push(Y_("Adhi (Chandra-Adhi)", "Lunar", adhi, [`${pyList(adhi)} in 6/7/8 from Moon`], [], "Phaladeepika ch.6; Saravali",
        "leadership, ministership, comfort, longevity", weak));
    }
    const am = BENEFICS.filter(p => c.house[p] === 10 || houseFrom(M, c.sign[p]) === 10);
    if (am.length) Y.push(Y_("Amala", "Reputation", am, [`${pyList(am)} in 10th from lagna or Moon`], [], "Phaladeepika ch.6",
      "spotless reputation, ethical conduct, prosperity"));
    const hm = houseFrom(c.sign.Jupiter, M);
    if ([6, 8, 12].includes(hm)) {
      const canc = [1, 4, 7, 10].includes(c.house.Moon) ? ["Moon in kendra from lagna (Phaladeepika ch.6)"] : [];
      Y.push(Y_("Shakata", "Dosha-yoga", ["Moon", "Jupiter"], [`Moon ${hm} from Jupiter`], canc, "Phaladeepika ch.6; Saravali",
        "ups and downs of fortune like a cart wheel"));
    }
    const vs = BENEFICS.filter(p => [3, 6, 10, 11].includes(c.house[p]) || [3, 6, 10, 11].includes(houseFrom(M, c.sign[p])));
    if (vs.length >= 2) Y.push(Y_("Vasumati", "Wealth", vs, [`benefics ${pyList(vs)} in upachaya from lagna/Moon`], [],
      "Phaladeepika ch.6", "steady accumulation of wealth"));
    const seen = new Set();
    for (const k of [1, 4, 7, 10]) for (const t of [5, 9]) {
      const a = c.lordOfHouse(k), b = c.lordOfHouse(t);
      if (a === b) {
        if (k !== 1 && !seen.has("self:" + a)) {
          seen.add("self:" + a);
          Y.push(Y_(`Yogakaraka ${a}`, "Raja", [a], [`${a} owns kendra ${k} and trikona ${t}`], [], "BPHS ch.34",
            "a single planet that gives raja yoga in its dasha", afflictions(c, a, comb, losers)));
        }
        continue;
      }
      const ways = c.connected(a, b);
      if (!ways.length) continue;
      const key = [a, b].sort().join("|");
      if (seen.has(key)) continue;
      seen.add(key);
      const weak = afflictions(c, a, comb, losers).concat(afflictions(c, b, comb, losers));
      for (const x of [a, b]) {
        const bad = c.housesOwned(x).filter(h => [6, 8, 12].includes(h));
        if (bad.length && !c.housesOwned(x).includes(1)) weak.push(`${x} also owns dusthana ${pyNums(bad)} (BPHS ch.39: raja yoga gives mixed results)`);
      }
      const label = (k === 10 && t === 9) ? "Dharma-Karmadhipati" : "Raja yoga";
      Y.push(Y_(label, "Raja", [a, b], [`lord of ${k} (${a}) and lord of ${t} (${b}): ${ways.join(", ")}`], [], "BPHS ch.39",
        "rise in status, authority, success - timed by dashas of these planets", weak));
    }
    const dh = new Set();
    for (const x of [2, 11]) for (const y of [1, 5, 9]) {
      const a = c.lordOfHouse(x), b = c.lordOfHouse(y);
      if (a !== b && c.connected(a, b).length) {
        const k = [a, b].sort().join("|");
        if (!dh.has(k)) {
          dh.add(k);
          Y.push(Y_("Dhana yoga", "Wealth", [a, b], [`lord ${x} (${a}) with lord ${y} (${b}): ${c.connected(a, b).join(", ")}`], [],
            "BPHS ch.41", "wealth accumulation in the periods of these planets",
            afflictions(c, a, comb, losers).concat(afflictions(c, b, comb, losers))));
        }
      }
    }
    for (const [h, n] of [[6, "Harsha"], [8, "Sarala"], [12, "Vimala"]]) {
      const lord = c.lordOfHouse(h);
      if ([6, 8, 12].includes(c.house[lord])) {
        const canc = c.housesOwned(lord).includes(1) ? [`${lord} is also lagna lord - its placement in a dusthana harms the self`] : [];
        const goodConj = c.conjunct(lord).filter(q => !c.housesOwned(q).every(x => [6, 8, 12].includes(x)) && q !== "Rahu" && q !== "Ketu");
        const weak = goodConj.length ? [`${lord} joined by non-dusthana lords ${pyList(goodConj)} - mixes results`] : [];
        const other = c.housesOwned(lord).filter(x => ![6, 8, 12].includes(x));
        if (other.length) weak.push(`${lord} also owns house(s) ${pyNums(other)}; those houses suffer from the dusthana placement`);
        Y.push(Y_(`${n} (Viparita Raja)`, "Viparita", [lord], [`${h}th lord ${lord} in house ${c.house[lord]}`], canc,
          "BPHS ch.39; Uttara Kalamrita", "success arising out of adversity / others' loss", weak));
      }
    }
    const done = new Set();
    for (const p of SEVEN) {
      const q = SIGN_LORD[c.sign[p]];
      if (q !== p && SEVEN.includes(q) && SIGN_LORD[c.sign[q]] === p && !done.has(q + "|" + p)) {
        done.add(p + "|" + q);
        const hs = [...new Set([c.house[p], c.house[q]])].sort((a, b) => a - b);
        const kind = hs.some(x => [6, 8, 12].includes(x)) ? "Dainya" : hs.includes(3) ? "Khala" : "Maha";
        const res = { Maha: "great prosperity and status", Dainya: "struggles, enemies, fluctuations", Khala: "fluctuating fortune; courage-driven gains" }[kind];
        Y.push(Y_(`${kind} Parivartana`, "Exchange", [p, q], [`${p} and ${q} exchange signs (houses ${pyNums(hs)})`], [], "Phaladeepika ch.6", res));
      }
    }
    for (const p of SEVEN) {
      if (c.dig[p] !== "Debilitated") continue;
      const s = c.sign[p], disp = SIGN_LORD[s], exLord = SIGN_LORD[exaltSign(p)];
      const exHere = SEVEN.filter(q => EXALTATION[q][0] === s);
      const conds = [];
      if (kendraFrom(c, disp, L) || kendraFrom(c, disp, M)) conds.push(`dispositor ${disp} in kendra from lagna/Moon (Phaladeepika ch.7) [strong]`);
      if (kendraFrom(c, exLord, L) || kendraFrom(c, exLord, M)) conds.push(`lord of exaltation sign ${exLord} in kendra from lagna/Moon (Phaladeepika ch.7) [strong]`);
      for (const q of exHere) if (kendraFrom(c, q, L) || kendraFrom(c, q, M)) conds.push(`${q} (exalted in ${SIGNS[s]}) in kendra from lagna/Moon (Phaladeepika ch.7) [strong]`);
      if (c.planetAspectedBy(p).includes(disp)) conds.push(`dispositor ${disp} aspects ${p} (Saravali) [medium]`);
      if (c.conjunct(p).includes(disp) || exHere.some(q => c.conjunct(p).includes(q))) conds.push("conjunct dispositor or the planet exalted in that sign [medium]");
      if (c.vargas[9][p] === exaltSign(p)) conds.push(`${p} exalted in navamsa (Jataka Parijata) [medium]`);
      if (c.retro(p)) conds.push(`${p} retrograde - some authors treat as strong (disputed) [weak]`);
      if (kendraFrom(c, p, L)) conds.push("debilitated planet itself in kendra from lagna [weak, popular]");
      const strong = conds.filter(x => x.includes("[strong]")).length;
      Y.push({ name: `Neecha Bhanga check: ${p}`, category: "Debility", planets: [p],
        conditions: conds.length ? conds : ["none of the cancellation conditions are met"], cancellations: [], weakenings: [],
        verdict: strong >= 2 ? "Neecha Bhanga Raja Yoga (strong cancellation)" : conds.length ? "Neecha Bhanga (cancelled debility)" : "Debility NOT cancelled",
        source: "Phaladeepika ch.7; BPHS; Saravali; Jataka Parijata",
        result: "a cancelled debility often gives a rise after initial struggle; an uncancelled one gives weak results for that planet's significations and houses" });
    }
    if (["Jupiter", "Venus", "Mercury"].every(p => [1, 2, 4, 5, 7, 9, 10].includes(c.house[p])) &&
        ["Exalted", "Own", "Moolatrikona", "Friend", "Great Friend"].includes(c.dig.Jupiter))
      Y.push(Y_("Saraswati", "Learning", ["Jupiter", "Venus", "Mercury"], ["Jupiter, Venus, Mercury in kendra/trikona/2nd; Jupiter strong"], [],
        "Phaladeepika ch.6", "learning, eloquence, poetry, fame in scholarship"));
    const l9 = c.lordOfHouse(9), l1 = c.lordOfHouse(1);
    if ([1, 4, 5, 7, 9, 10].includes(c.house[l9]) && ["Exalted", "Own", "Moolatrikona"].includes(c.dig[l9]) &&
        ((shad.planets[l1] || { ratio: 1 }).ratio >= 1))
      Y.push(Y_("Lakshmi", "Wealth", [l9], [`9th lord ${l9} ${c.dig[l9]} in kendra/trikona, lagna lord strong`], [], "BPHS ch.41", "wealth, nobility, fortune"));
    for (const [ref, name] of [[L, "Lagna"], [M, "Moon"]]) {
      const b12 = PLANETS.filter(p => houseFrom(ref, c.sign[p]) === 12 && p !== "Moon");
      const b2 = PLANETS.filter(p => houseFrom(ref, c.sign[p]) === 2 && p !== "Moon");
      if (b12.length && b2.length) {
        const all = b12.concat(b2);
        if (all.every(p => BENEFICS.includes(p))) Y.push(Y_(`Shubha Kartari (${name})`, "Kartari", all, [`${name} hemmed by benefics`], [], "Phaladeepika ch.6", "protection, health, prosperity for that point"));
        else if (all.every(p => MALEFICS.includes(p))) Y.push(Y_(`Papa Kartari (${name})`, "Kartari", all, [`${name} hemmed by malefics`], [], "Phaladeepika ch.6", "pressure, obstacles and health issues for that point"));
      }
    }
    const day = c.sun.is_day, three = [L, c.sign.Sun, M];
    const odd = three.every(s => s % 2 === 0), even = three.every(s => s % 2 === 1), g = c.birth.gender;
    if ((g === "M" && day && odd) || (g === "F" && !day && even))
      Y.push(Y_("Mahabhagya", "Fortune", ["Sun", "Moon"], ["day birth with Lagna/Sun/Moon in odd signs (male) or night birth with even signs (female)"], [],
        "BPHS; Phaladeepika ch.6", "great fortune, long life, fame"));
    const occ = new Set(SEVEN.map(p => c.sign[p])).size;
    const sank = { 7: "Vallaki/Veena", 6: "Dama", 5: "Pasha", 4: "Kedara", 3: "Shoola", 2: "Yuga", 1: "Gola" };
    const sres = { 7: "many friends, arts, happiness", 6: "generous, helpful, wealthy", 5: "skilled earner, many dependants",
      4: "agriculture/land, useful to others", 3: "sharp, may be harsh, struggles", 2: "unconventional, may lack wealth", 1: "poverty or extreme focus" };
    Y.push(Y_(`${sank[occ]} (Sankhya Nabhasa)`, "Nabhasa", [...SEVEN], [`7 planets occupy ${occ} signs`], [], "BPHS ch.35",
      sres[occ] + " (Nabhasa yogas give a background tone, not specific events)"));
    if ([1, 4, 7, 10].every(h => c.occupants(h).length))
      Y.push(Y_("Chatussagara", "Fame", [], ["all four kendras occupied"], [], "Phaladeepika ch.6", "fame across the four seas, wealth, longevity"));
    return Y;
  }

  // ---------------------------------------------------------------- doshas
  const KAAL_SARP = { 1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal", 5: "Padma", 6: "Mahapadma", 7: "Takshak", 8: "Karkotak",
    9: "Shankhachood", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag" };
  const D_ = (name, present, details, cancellations, classical, effect, severity = null) => ({
    name, present, status: !present ? "absent" : cancellations.length ? "present but cancelled/reduced" : "present",
    details, cancellations, classical_status: classical, effect, severity });
  function mangalDosha(c) {
    const refs = { Lagna: c.lagna, Moon: c.moonSign, Venus: c.sign.Venus }, hits = {};
    for (const [k, v] of Object.entries(refs)) { const h = houseFrom(v, c.sign.Mars); if ([1, 2, 4, 7, 8, 12].includes(h)) hits[k] = h; }
    const canc = [], ms = c.sign.Mars, h = c.house.Mars;
    if (ms === 0 || ms === 7) canc.push("Mars in own sign (Aries/Scorpio)");
    if (ms === 9) canc.push("Mars exalted (Capricorn)");
    if (c.conjunct("Mars").includes("Jupiter") || c.planetAspectedBy("Mars").includes("Jupiter")) canc.push("Jupiter conjoins/aspects Mars");
    if (c.conjunct("Mars").includes("Moon")) canc.push("Mars with Moon (Chandra-Mangala)");
    const popular = { 2: [2, 5], 12: [1, 6], 4: [0, 7], 7: [3, 9], 8: [8, 11], 1: [4, 10] };
    if (popular[h] && popular[h].includes(ms)) canc.push(`Mars in house ${h} in ${SIGNS[ms]} (popular regional exception list)`);
    if (c.house.Jupiter === 1 || c.house.Venus === 1) canc.push("Jupiter or Venus in lagna");
    const n = Object.keys(hits).length;
    return D_("Mangal (Kuja) Dosha", n > 0, { from: hits, mars_house_from_lagna: h,
      note: "Matching practice: dosha is neutralised if the partner has a comparable dosha." }, n ? canc : [],
      "Not in BPHS as a named dosha; comes from muhurta/marriage-matching literature and regional practice",
      "friction, delay or strain in marriage; Mars energy needs a channel", n ? (n === 3 ? "high" : n === 2 ? "medium" : "low") : null);
  }
  function kaalSarp(c) {
    const r = c.lon.Rahu;
    const sides = SEVEN.map(p => J.Astro.norm(c.lon[p] - r) < 180);
    const cnt = sides.filter(Boolean).length;
    const full = cnt === 7 || cnt === 0;
    const outside = SEVEN.filter((p, i) => sides[i] !== (cnt >= 4));
    const partial = outside.length === 1, present = full || partial;
    const canc = [];
    if (partial) canc.push(`partial: ${outside[0]} is outside the Rahu-Ketu axis`);
    if (present) {
      const conj = SEVEN.filter(p => c.conjunct("Rahu").includes(p) || c.conjunct("Ketu").includes(p));
      if (conj.length) canc.push(`${pyList(conj)} conjunct a node - many practitioners consider the yoga broken by a planet on the axis`);
    }
    return D_(present ? `Kaal Sarp (${KAAL_SARP[c.house.Rahu]})` : "Kaal Sarp", present,
      { rahu_house: c.house.Rahu, direction: cnt >= 4 ? "Rahu->Ketu" : "Ketu->Rahu" }, canc,
      "NOT in BPHS, Brihat Jataka, Saravali or Phaladeepika - a later/popular combination",
      "phases of obstruction followed by sudden rise; never used alone to predict events");
  }
  function pairDoshas(c) {
    const specs = [
      ["Grahan Dosha (Sun)", "Sun", ["Rahu", "Ketu"], "eclipse of Sun: father, ego, authority, health", "Popular; BPHS ch.83 mentions Sun-node afflictions among causes of curses (shapa)"],
      ["Grahan Dosha (Moon)", "Moon", ["Rahu", "Ketu"], "eclipse of Moon: anxiety, mother, emotional instability", "Popular; Moon-node results in Saravali/BPHS"],
      ["Guru Chandal", "Jupiter", ["Rahu", "Ketu"], "ethics/guru/children issues, unorthodox beliefs", "Popular name; Jupiter-Rahu conjunction results are classical"],
      ["Shrapit", "Saturn", ["Rahu"], "delays, karmic burdens", "Modern/popular combination, not classical"],
      ["Angarak", "Mars", ["Rahu", "Ketu"], "anger, accidents, impulsive acts", "Popular"],
      ["Vish Yoga", "Moon", ["Saturn"], "depressive tendencies, emotional heaviness, delays", "Popular; Moon-Saturn conjunction results described in Saravali"],
    ];
    return specs.map(([name, a, bs, eff, cls]) => {
      const hit = bs.filter(b => c.conjunct(a).includes(b)), canc = [];
      if (hit.length && a !== "Jupiter" && c.planetAspectedBy(a).includes("Jupiter")) canc.push("Jupiter aspects the afflicted planet");
      if (hit.length && ["Exalted", "Own", "Moolatrikona"].includes(c.dig[a])) canc.push(`${a} strong by sign (${c.dig[a]})`);
      return D_(name, hit.length > 0, { with: hit, house: hit.length ? c.house[a] : null }, canc, cls, eff);
    });
  }
  function pitruDosha(c) {
    const reasons = [], l9 = c.lordOfHouse(9);
    for (const x of ["Rahu", "Ketu", "Saturn"]) {
      if (c.conjunct("Sun").includes(x)) reasons.push(`Sun with ${x}`);
      if (c.house[x] === 9) reasons.push(`${x} in 9th house`);
      if (c.conjunct(l9).includes(x) && l9 !== x) reasons.push(`9th lord ${l9} with ${x}`);
    }
    const canc = reasons.length && (c.aspectedBy(9).includes("Jupiter") || c.house.Jupiter === 9) ? ["Jupiter aspects/occupies the 9th house"] : [];
    return D_("Pitru Dosha", reasons.length > 0, { reasons }, canc,
      "Based on BPHS ch.83-84 (curses from past life: pitri shapa) as summarised by later authors",
      "obstacles linked to father/ancestors, progeny delays, fortune blocked until remedies");
  }
  function gandmool(c) {
    const n = nakshatraOf(c.lon.Moon), present = GANDMOOL.includes(n.name);
    let sev = null;
    if (present) sev = n.pada === (["Ashlesha", "Jyeshtha", "Revati"].includes(n.name) ? 4 : 1) ? "high (junction pada)" : "mild";
    return D_("Gandmool", present, { moon_nakshatra: n.name, pada: n.pada }, [],
      "Muhurta tradition (e.g. Muhurta Chintamani); Shanti traditionally done on the 27th day",
      "early-life health/family disturbances per pada; mostly a birth-time ritual concern", sev);
  }
  const doshas = c => [mangalDosha(c), kaalSarp(c), pitruDosha(c), gandmool(c)].concat(pairDoshas(c));

  // ---------------------------------------------------------------- jaimini
  const K7 = ["Atmakaraka (self/soul)", "Amatyakaraka (career/advisor)", "Bhratrikaraka (siblings/guru)", "Matrikaraka (mother)",
    "Putrakaraka (children)", "Gnatikaraka (rivals/disease)", "Darakaraka (spouse)"];
  const K8 = K7.slice(0, 4).concat(["Pitrikaraka (father)"], K7.slice(4));
  function charaKarakas(c, count) {
    const degs = {};
    for (const p of SEVEN) degs[p] = c.lon[p] % 30;
    if (count === 8) degs.Rahu = 30 - (c.lon.Rahu % 30);
    const order = Object.keys(degs).sort((a, b) => degs[b] - degs[a]);
    const names = count === 8 ? K8 : K7;
    return order.map((p, i) => ({ karaka: names[i], planet: p, degree_used: round(degs[p], 3) }));
  }
  function dualLord(c, sign) {
    let pair;
    if (sign === 7) pair = ["Mars", "Ketu"]; else if (sign === 10) pair = ["Saturn", "Rahu"]; else return SIGN_LORD[sign];
    const [a, b] = pair, ca = c.conjunct(a).length, cb = c.conjunct(b).length;
    if (ca !== cb) return ca > cb ? a : b;
    return c.lon[a] % 30 >= c.lon[b] % 30 ? a : b;
  }
  function arudha(c, house) {
    const hs = (c.lagna + house - 1) % 12, lord = dualLord(c, hs);
    const n = houseFrom(hs, c.sign[lord]);
    let pada = (c.sign[lord] + n - 1) % 12;
    if (pada === hs || pada === (hs + 6) % 12) pada = (pada + 9) % 12;
    return pada;
  }
  function horaLagna(c) {
    const snap = J.Astro.snapshot(c.sun.sunrise);
    return J.Astro.norm(snap.bodies.Sun.lon + (c.jd - c.sun.sunrise) * 24 * 30);
  }
  function span(a, b) {
    const m = new Set([MODALITY[a], MODALITY[b]]);
    const eq = (...x) => m.size === x.length && x.every(v => m.has(v));
    if (eq("Movable") || eq("Fixed", "Dual")) return "Long (Purna)";
    if (eq("Movable", "Fixed") || eq("Dual")) return "Medium (Madhya)";
    return "Short (Alpa)";
  }
  function longevity(c) {
    const l1 = c.lordOfHouse(1), l8 = c.lordOfHouse(8), hl = J.signOf(horaLagna(c));
    const pairs = [
      { pair: `Lagna lord ${l1} & 8th lord ${l8}`, span: span(c.sign[l1], c.sign[l8]) },
      { pair: "Lagna & Moon sign", span: span(c.lagna, c.moonSign) },
      { pair: `Lagna & Hora Lagna (${SIGNS[hl]})`, span: span(c.lagna, hl) },
    ];
    const spans = pairs.map(p => p.span);
    const counts = {}; spans.forEach(s => counts[s] = (counts[s] || 0) + 1);
    let best = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0], rule = "majority of the three pairs";
    if (counts[best] === 1) { best = pairs[2].span; rule = "all three differ: Lagna-Hora Lagna pair decides (Jaimini 2.1 commentary)"; }
    const order = ["Short (Alpa)", "Medium (Madhya)", "Long (Purna)"], modifiers = [];
    if ((c.house.Jupiter === 1 || c.house.Jupiter === 7) && c.dig.Jupiter !== "Debilitated") {
      modifiers.push("Jupiter in lagna/7th unafflicted: longevity raised one compartment (kakshya vriddhi)");
      best = order[Math.min(order.indexOf(best) + 1, 2)];
    }
    if ((l1 === "Saturn" || l8 === "Saturn") && !["Exalted", "Own", "Moolatrikona"].includes(c.dig.Saturn))
      modifiers.push("Saturn is one of the deciding lords: commentators reduce within the compartment (kakshya hrasa) - applied as a caution only");
    return { pairs, category: best, rule_used: rule, modifiers,
      ranges_years: { "Short (Alpa)": "up to ~32-36", "Medium (Madhya)": "~32/36 to ~64/72", "Long (Purna)": "~64/72 to ~96-108" },
      caution: "Classical texts (BPHS ch.44) themselves warn that longevity is the hardest judgement; this compartment is one indicator among several and is never converted into a date." };
  }
  function jaimini(c) {
    const n = c.settings.chara_karaka_count, k7 = charaKarakas(c, 7), k8 = charaKarakas(c, 8);
    const active = n === 8 ? k8 : k7;
    const differ = k7.some((a, i) => a.planet !== k8[i].planet);
    const padas = {};
    for (let h = 1; h <= 12; h++) {
      const s = arudha(c, h);
      const label = { 1: "Arudha Lagna (AL - image/status)", 12: "Upapada (UL - marriage)" }[h] || `A${h}`;
      padas[label] = { sign: SIGNS[s], house_from_lagna: houseFrom(c.lagna, s), occupants: PLANETS.filter(p => c.sign[p] === s) };
    }
    const ak = active[0].planet, ks = c.vargas[9][ak];
    return { chara_karakas: active, scheme: `${n}-karaka (default ${n})`, other_scheme_differs: differ, other_scheme: n === 7 ? k8 : k7,
      arudha_padas: padas, karakamsha: { atmakaraka: ak, karakamsha_sign: SIGNS[ks],
        planets_in_karakamsha_in_d9: PLANETS.filter(p => c.vargas[9][p] === ks),
        "12th_from_karakamsha_d9": PLANETS.filter(p => c.vargas[9][p] === (ks + 11) % 12) },
      longevity: longevity(c) };
  }

  // ---------------------------------------------------------------- profiles
  const PLANET_LOOKS = {
    Sun: "square/medium build, honey-coloured eyes, little hair, dark-red/copper complexion, commanding",
    Moon: "round face/body, fair complexion, soft and attractive eyes, gentle speech, changeable",
    Mars: "youthful, medium-tall, thin waist, reddish complexion, sharp eyes; marks/scars or cuts",
    Mercury: "slim, well-proportioned, greenish/wheatish (durva-grass) tone, witty, youthful-looking",
    Jupiter: "large or heavy body, yellowish/golden tone, good eyes and hair, dignified",
    Venus: "attractive, large beautiful eyes, curly/dark hair, mixed (variegated) complexion, charming",
    Saturn: "lean and tall, dark complexion, coarse hair, prominent teeth/joints, looks older",
    Rahu: "smoky/dark tone, tall, unconventional looks, possibly foreign/different background",
    Ketu: "thin, rough skin, marks/scars, unusual or intense features",
  };
  const SIGN_LOOKS = { 0: "medium height, lean, round eyes, mark on head likely", 1: "well-built, broad face/thighs, attractive",
    2: "tall-ish, long arms, expressive eyes", 3: "medium/short, plump, quick gait", 4: "broad face and chest, large build, tawny eyes",
    5: "slim, graceful, modest, youthful face", 6: "tall, well-proportioned, prominent nose", 7: "medium, broad eyes and chest, strong body",
    8: "long face and neck, well-built", 9: "slender, weak lower limbs, deep eyes", 10: "tall, lean, prominent veins",
    11: "medium, well-proportioned, fish-like eyes, fair" };
  const BODY = { 1: "head/forehead", 2: "face", 3: "neck/arms", 4: "chest", 5: "stomach", 6: "waist/abdomen", 7: "lower abdomen",
    8: "private parts", 9: "thighs", 10: "knees", 11: "calves", 12: "feet" };
  const MALE_SIGNS = [0, 2, 4, 6, 8, 10];
  function spouseProfile(c) {
    const h7 = (c.lagna + 6) % 12, lord = SIGN_LORD[h7], occ = c.occupants(7);
    const asp = c.aspectedBy(7, true).filter(p => !occ.includes(p));
    const karaka = c.birth.gender === "F" ? "Jupiter" : "Venus";
    const d9_7 = (c.vargas[9].Lagna + 6) % 12, d9occ = PLANETS.filter(p => c.vargas[9][p] === d9_7);
    const ind = [{ factor: `7th sign ${SIGNS[h7]}`, suggests: SIGN_LOOKS[h7], weight: "high" },
      { factor: `7th lord ${lord} in ${SIGNS[c.sign[lord]]} (house ${c.house[lord]})`, suggests: PLANET_LOOKS[lord], weight: "high" }];
    occ.forEach(p => ind.push({ factor: `${p} in 7th`, suggests: PLANET_LOOKS[p], weight: "highest" }));
    asp.forEach(p => ind.push({ factor: `${p} aspects 7th`, suggests: PLANET_LOOKS[p], weight: "medium" }));
    ind.push({ factor: `D9 7th sign ${SIGNS[d9_7]}`, suggests: SIGN_LOOKS[d9_7], weight: "high" });
    d9occ.forEach(p => ind.push({ factor: `${p} in D9 7th`, suggests: PLANET_LOOKS[p], weight: "high" }));
    ind.push({ factor: `karaka ${karaka} in ${SIGNS[c.sign[karaka]]}`, suggests: PLANET_LOOKS[karaka], weight: "medium" });
    const marks = [];
    for (const p of ["Mars", "Saturn", "Ketu", "Rahu"]) if (occ.includes(p) || asp.includes(p)) {
      const hf = houseFrom(h7, c.sign[p]);
      marks.push(`${p} influences the 7th: a mark/scar/injury is indicated on the spouse; body region by the sign it occupies counted from the 7th (Kalapurusha) - ${p} is in sign ${SIGNS[c.sign[p]]}, ${hf} from the 7th = ${BODY[hf]}`);
    }
    const lh = c.house[lord];
    const dir = [1, 4, 7, 10].includes(lh) ? "near (kendra)" : [2, 5, 8, 11].includes(lh) ? "moderate distance" : "far / possibly foreign";
    return { indicators: ind, marks, distance_of_spouse_origin: `7th lord in house ${lh}: ${dir} (popular rule)`,
      darakaraka_note: "See jaimini.chara_karakas for Darakaraka; its sign/nakshatra add to the description",
      method: "Describe by combining: planets IN the 7th (strongest) > 7th lord > D9 7th > aspects > karaka. Where indicators conflict, say so." };
  }
  function childrenProfile(c) {
    const h5 = (c.lagna + 4) % 12, lord = SIGN_LORD[h5], occ = c.occupants(5);
    const d7l = c.vargas[7].Lagna, d7_5 = (d7l + 4) % 12, loss = [];
    for (const p of occ) if (["Mars", "Saturn", "Rahu", "Ketu"].includes(p))
      loss.push(`${p} in 5th (BPHS progeny chapter: malefic in 5th troubles progeny; Rahu/Ketu/Mars may indicate loss of pregnancy or surgery-related birth)`);
    if ([6, 8, 12].includes(c.house[lord])) loss.push(`5th lord ${lord} in dusthana ${c.house[lord]} - delays/obstacles to progeny`);
    if (c.dig[lord] === "Debilitated") loss.push(`5th lord ${lord} debilitated`);
    if (["Debilitated", "Enemy", "Great Enemy"].includes(c.dig.Jupiter) || [6, 8, 12].includes(c.house.Jupiter))
      loss.push(`putrakaraka Jupiter weak (${c.dig.Jupiter}, house ${c.house.Jupiter})`);
    const ma = c.aspectedBy(5, true).filter(p => p === "Mars" || p === "Saturn");
    if (ma.length) loss.push(`5th aspected by ${pyList(ma)}`);
    const sex = occ.concat([lord]).map(p => `${p}: ${["Sun", "Mars", "Jupiter"].includes(p) ? "male" : ["Moon", "Venus"].includes(p) ? "female" : "neuter (follows sign)"}`);
    sex.push(`5th sign ${SIGNS[h5]}: ${MALE_SIGNS.includes(h5) ? "male" : "female"}`);
    sex.push(`D7 5th sign ${SIGNS[d7_5]}: ${MALE_SIGNS.includes(d7_5) ? "male" : "female"}`);
    const nav = Math.floor((c.lon[lord] % 30) / (30 / 9)) + 1;
    return { fifth_house: SIGNS[h5], fifth_lord: lord, occupants: occ, d7_lagna: SIGNS[d7l], d7_fifth: SIGNS[d7_5],
      d7_fifth_occupants: PLANETS.filter(p => c.vargas[7][p] === d7_5), gender_indicators: sex, pregnancy_obstacle_indicators: loss,
      count_indicators: [`5th lord ${lord} has crossed ${nav} navamsha(s) in its sign - an old rule gives the count of children by navamshas (Phaladeepika ch.12); treat as a rough indicator only`],
      method: "Order of children: 5th house = 1st child, 7th = 2nd, 9th = 3rd (each 3rd from previous) - judge each with its lord; time each with dasha of those significators + Jupiter transit." };
  }
  function careerProfile(c) {
    const l10 = c.lordOfHouse(10), occ = c.occupants(10), d10_10 = (c.vargas[10].Lagna + 9) % 12;
    const fields = { Sun: "government, administration, politics, medicine, authority roles", Moon: "public dealing, hospitality, nursing, food, liquids, travel, psychology",
      Mars: "army/police, engineering, surgery, real estate, sports, machinery", Mercury: "commerce, accounts, IT, writing, media, teaching, analysis",
      Jupiter: "teaching, law, finance/banking, advisory, religion, management", Venus: "arts, fashion, beauty, entertainment, luxury goods, hospitality, vehicles",
      Saturn: "labour-intensive industry, mining, oil, service/large organisations, judiciary, construction", Rahu: "technology, foreign companies, aviation, unconventional/new fields, research",
      Ketu: "research, spirituality, coding/occult, isolated technical work" };
    const nd = SIGN_LORD[c.vargas[9][l10]], govt = [];
    if ([1, 10, 11, 9].includes(c.house.Sun) && c.dig.Sun !== "Debilitated") govt.push(`Sun in house ${c.house.Sun}`);
    if (occ.includes("Sun") || l10 === "Sun") govt.push("Sun linked to 10th");
    if (c.house.Moon === 10) govt.push("Moon in 10th");
    const fi = {};
    for (const p of occ.concat([l10, nd])) fi[p] = fields[p];
    return { tenth_sign: SIGNS[(c.lagna + 9) % 12], tenth_lord: l10, occupants: occ, field_indicators: fi, d10_tenth: SIGNS[d10_10],
      d10_tenth_occupants: PLANETS.filter(p => c.vargas[10][p] === d10_10), navamsa_dispositor_of_10th_lord: nd, govt_job_indicators: govt,
      self_employed_vs_service: [3, 7, 11].includes(c.house[l10]) ? "business tendency (7th/3rd strong, Mercury/Venus to 10th)"
        : [6, 10].includes(c.house[l10]) ? "service tendency (6th/10th/Saturn link)" : "mixed - judge with D10",
      method: "Profession by: planets in 10th, 10th lord, navamsa dispositor of 10th lord (Phaladeepika ch.5), D10, Amatyakaraka." };
  }
  function mindProfile(c) {
    const m = [], conj = c.conjunct("Moon");
    for (const p of ["Saturn", "Rahu", "Ketu", "Mars"]) {
      if (conj.includes(p)) m.push(`Moon with ${p}`);
      if (c.planetAspectedBy("Moon").includes(p)) m.push(`${p} aspects Moon`);
    }
    if (["Debilitated", "Enemy", "Great Enemy"].includes(c.dig.Moon)) m.push(`Moon ${c.dig.Moon}`);
    if ([6, 8, 12].includes(c.house.Moon)) m.push(`Moon in dusthana ${c.house.Moon}`);
    const el = J.Astro.norm(c.lon.Moon - c.lon.Sun);
    if (el < 72 || el > 288) m.push("dark (weak) Moon near amavasya");
    if (c.dig.Mercury === "Debilitated" || c.conjunct("Mercury").includes("Rahu")) m.push("Mercury afflicted (overthinking/nervous stress)");
    const good = [];
    if (c.planetAspectedBy("Moon").includes("Jupiter") || conj.includes("Jupiter")) good.push("Jupiter protects the Moon");
    if (["Exalted", "Own", "Moolatrikona"].includes(c.dig.Moon)) good.push(`Moon ${c.dig.Moon}`);
    if ([1, 4, 7, 10, 5, 9].includes(c.house.Moon)) good.push(`Moon in good house ${c.house.Moon}`);
    return { stressors: m, stabilisers: good, moon_nakshatra: nakshatraOf(c.lon.Moon).name, fourth_lord: c.lordOfHouse(4),
      fourth_lord_house: c.house[c.lordOfHouse(4)] };
  }
  const profiles = c => ({ spouse: spouseProfile(c), children: childrenProfile(c), career: careerProfile(c), mind: mindProfile(c) });

  // ---------------------------------------------------------------- remedies
  const GEMS = {
    Sun: { gem: "Ruby (Manik)", upratna: "Red garnet / red spinel", finger: "ring", metal: "gold or copper", day: "Sunday morning (Sun hora)", weight: "3-5 carat", alt_finger: null },
    Moon: { gem: "Pearl (Moti)", upratna: "Moonstone", finger: "little", metal: "silver", day: "Monday evening / Shukla paksha", weight: "5-7 carat", alt_finger: "ring" },
    Mars: { gem: "Red Coral (Moonga)", upratna: "Carnelian", finger: "ring", metal: "gold or copper", day: "Tuesday morning", weight: "6-9 carat", alt_finger: null },
    Mercury: { gem: "Emerald (Panna)", upratna: "Peridot / green tourmaline", finger: "little", metal: "gold or bronze", day: "Wednesday morning", weight: "3-6 carat", alt_finger: null },
    Jupiter: { gem: "Yellow Sapphire (Pukhraj)", upratna: "Citrine / yellow topaz", finger: "index", metal: "gold", day: "Thursday morning", weight: "3-5 carat", alt_finger: null },
    Venus: { gem: "Diamond (Heera)", upratna: "White sapphire / zircon / opal", finger: "middle", metal: "silver or platinum", day: "Friday morning", weight: "0.5-1 carat (white sapphire 3-5)", alt_finger: "ring (many practitioners) - finger rule differs by tradition" },
    Saturn: { gem: "Blue Sapphire (Neelam)", upratna: "Amethyst / iolite", finger: "middle", metal: "silver, panchdhatu or iron", day: "Saturday evening", weight: "3-5 carat", alt_finger: null },
    Rahu: { gem: "Hessonite (Gomed)", upratna: "Orange zircon", finger: "middle", metal: "silver or panchdhatu", day: "Saturday evening", weight: "5-8 carat", alt_finger: null },
    Ketu: { gem: "Cat's Eye (Lehsunia)", upratna: "Tiger's eye", finger: "little", metal: "silver", day: "Tuesday or Thursday", weight: "3-5 carat", alt_finger: "ring (some traditions)" },
  };
  const MANTRA = {
    Sun: ["ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", 7000, "Aditya Hridayam; offer water at sunrise", "wheat, jaggery, copper, red cloth - Sunday"],
    Moon: ["ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः", 11000, "Shiva worship; serve mother", "rice, milk, silver, white cloth - Monday"],
    Mars: ["ॐ क्रां क्रीं क्रौं सः भौमाय नमः", 10000, "Hanuman Chalisa; Kartikeya", "masoor dal, jaggery, red cloth - Tuesday"],
    Mercury: ["ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", 9000, "Vishnu Sahasranama", "green moong, green cloth, feed cows green fodder - Wednesday"],
    Jupiter: ["ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", 19000, "respect teachers/elders; Vishnu", "chana dal, turmeric, yellow cloth, books - Thursday"],
    Venus: ["ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", 16000, "Lakshmi/Durga worship", "rice, ghee, curd, white cloth, perfume - Friday"],
    Saturn: ["ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", 23000, "Shani stotra; Hanuman; serve workers", "black sesame, mustard oil, iron, black cloth - Saturday"],
    Rahu: ["ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः", 18000, "Durga Saptashati", "urad, blanket, coconut - Saturday"],
    Ketu: ["ॐ स्रां स्रीं स्रौं सः केतवे नमः", 17000, "Ganesha worship", "multi-coloured blanket, sesame, feed dogs - Tuesday/Saturday"],
  };
  function enemies(p) {
    let e = NATURAL_FRIENDS[p] ? new Set(NATURAL_FRIENDS[p].enemies) : new Set(["Sun", "Moon"]);
    if (p === "Sun" || p === "Moon") { e.add("Rahu"); e.add("Ketu"); }
    return e;
  }
  function gemAdvice(c, func, cond, shad, comb) {
    const recs = [];
    for (const p of PLANETS) {
      const f = func.planets[p], verdict = f.verdict, owned = f.owns, reasons = [], cautions = [];
      const deg = c.lon[p] % 30, av = baladiAvastha(c.sign[p], deg);
      let status;
      if (p === "Rahu" || p === "Ketu") {
        status = "avoid unless specifically indicated";
        if ([3, 6, 10, 11].includes(c.house[p])) { status = "conditional (trial first)"; reasons.push(`${p} in upachaya house ${c.house[p]} gives good results`); }
        cautions.push("node gems act fast and unpredictably - 3-day trial (keep under pillow) is customary");
      } else if (verdict.startsWith("Benefic") || verdict.startsWith("Yogakaraka")) {
        const weak = [];
        if (shad.planets[p].ratio < 1) weak.push(`shadbala ${pyNum(shad.planets[p].ratio)}x of required`);
        if (["Debilitated", "Enemy", "Great Enemy"].includes(c.dig[p])) weak.push(`dignity ${c.dig[p]}`);
        if (comb[p]) weak.push("combust");
        if (/^(Mrita|Bala|Vriddha)/.test(av)) weak.push(`degree state ${av}`);
        if (weak.length) { status = "recommended (functional benefic that is weak)"; reasons.push(`${verdict}; owns houses ${pyNums(owned)}`, ...weak); }
        else { status = "optional (functional benefic already strong)"; reasons.push(`${verdict}; already strong - gem adds little`); }
        if ([6, 8, 12].includes(c.house[p])) cautions.push(`placed in dusthana ${c.house[p]} - a gem also amplifies that house's troubles; many practitioners prefer mantra/daan here`);
        if (c.dig[p] === "Debilitated") cautions.push("debilitated: traditions differ on gems for debilitated planets (check the Neecha Bhanga result)");
        if (owned.includes(2) || owned.includes(7)) cautions.push("also a maraka (2nd/7th lord) - watch health during its periods");
      } else if (verdict.startsWith("Malefic")) {
        status = "avoid";
        reasons.push(`functional malefic for this lagna (owns ${pyNums(owned)}) - strengthening it strengthens problems`);
      } else {
        status = "neutral - only if strongly indicated by a specific problem";
        reasons.push(`${verdict}; owns ${pyNums(owned)}`);
      }
      if (deg < 1 || deg > 29) cautions.push("planet at a sign junction (rashi sandhi) - results erratic, gem effect uncertain");
      recs.push({ planet: p, status, ...GEMS[p], reasons, cautions });
    }
    const wear = recs.filter(r => /^(recommended|optional)/.test(r.status)), conflicts = [];
    wear.forEach((a, i) => wear.slice(i + 1).forEach(b => {
      if (enemies(a.planet).has(b.planet) || enemies(b.planet).has(a.planet))
        conflicts.push(`${a.gem} (${a.planet}) and ${b.gem} (${b.planet}) are natural enemies - do not wear together; choose the one for the more important house/dasha`);
      else if (a.finger === b.finger) conflicts.push(`${a.gem} and ${b.gem} share the ${a.finger} finger - wear on separate hands or pick one`);
    }));
    return { recommendations: recs, conflicts, general_rules: [
      "Gems strengthen a planet, they do not make a malefic good. Lagna lord, 5th and 9th lords and a yogakaraka are the usual candidates; lords of 3, 6, 8, 11 are avoided unless they also own a trikona.",
      "The gem of the running mahadasha/antardasha lord is considered only if that lord is a functional benefic.",
      "Natural gems of good clarity; weight scales with body weight in most traditions.",
      "Wear on the working hand on the planet's day/hora after energising with its mantra (108 times).",
      "The classical texts (BPHS etc.) prescribe mantra, daan and worship; gem therapy is from later Ratna-shastra and modern practice.",
    ] };
  }
  function mantraDaan(c, func, cond) {
    const out = [];
    for (const p of PLANETS) {
      const weak = cond[p].net < 0, mal = func.planets[p].verdict.startsWith("Malefic") || p === "Rahu" || p === "Ketu";
      if (weak || mal) {
        const [m, n, deity, daan] = MANTRA[p];
        out.push({ planet: p, why: (weak ? "weak" : "") + (weak && mal ? " & " : "") + (mal ? "functional malefic / node" : ""),
          beej_mantra: m, japa_count: n, worship: deity, daan });
      }
    }
    return out;
  }
  const LK_PAKKA = { Sun: [1], Moon: [4], Mars: [3, 8], Mercury: [7], Jupiter: [2, 5, 9, 12], Venus: [7], Saturn: [8, 10], Rahu: [12], Ketu: [6] };
  const LK_EXALT = { Sun: [1], Moon: [2], Mars: [10], Mercury: [6], Jupiter: [4], Venus: [12], Saturn: [7], Rahu: [3, 6], Ketu: [9, 12] };
  const LK_DEBIL = { Sun: [7], Moon: [8], Mars: [4], Mercury: [12], Jupiter: [10], Venus: [6], Saturn: [1], Rahu: [8, 9], Ketu: [3, 6] };
  const LK_ASPECT = { 1: [7], 2: [6], 3: [9, 11], 4: [10], 5: [9], 6: [12], 8: [2] };
  const LK_GENERAL = {
    Sun: "offer water to the rising Sun; flow a copper coin in running water; avoid taking things for free",
    Moon: "serve mother and take her blessings; keep silver; keep a vessel of water/milk by the bed at night and pour it on a tree in the morning",
    Mars: "distribute sweets; keep a red handkerchief; respect brothers; feed sweet roti to animals",
    Mercury: "feed green fodder to cows; respect sisters/daughters/aunts; avoid green clothing if Mercury is bad",
    Jupiter: "apply saffron/turmeric tilak; serve elders and teachers; water a peepal tree",
    Venus: "respect spouse; donate curd/ghee/camphor; feed cows",
    Saturn: "feed crows; offer mustard oil; avoid alcohol and meat; serve labourers; keep honesty in dealings",
    Rahu: "flow coal or barley in running water; keep a solid silver ball; avoid blue clothes and liquor",
    Ketu: "feed dogs; donate a black-white blanket; respect sons/nephews; wear gold in the ear (traditional)",
  };
  const LK_RIN = [
    ["Pitru Rin (ancestral debt)", h => ["Venus", "Mercury", "Rahu"].filter(p => [2, 5, 9, 12].includes(h[p])), "collect money from every family member and donate together on one day"],
    ["Matri Rin (mother's debt)", h => h.Ketu === 4 ? ["Ketu"] : [], "collect silver from family members and flow it in running water"],
    ["Stri Rin (debt to women)", h => ["Sun", "Rahu", "Ketu"].filter(p => [2, 7].includes(h[p])), "feed 100 cows on one day with family contribution"],
    ["Sambandhi Rin (relatives)", h => ["Mercury", "Ketu"].filter(p => [1, 8].includes(h[p])), "help a relative's family at a ceremony with joint contribution"],
    ["Behen/Beti Rin (sister/daughter)", h => [3, 6].includes(h.Moon) ? ["Moon"] : [], "distribute yellow cowries/sweets to girls with family contribution"],
    ["Nirdayi Rin (cruelty)", h => ["Sun", "Moon", "Mars"].filter(p => [10, 11].includes(h[p])), "feed 100 labourers in one day with family contribution"],
    ["Ajanma Rin (unborn)", h => ["Sun", "Venus", "Mars"].filter(p => h[p] === 12), "collect coconuts from family members and flow in water"],
  ];
  function lalKitab(c) {
    const h = c.house;
    const rows = PLANETS.map(p => ({ planet: p, lk_house: h[p],
      state: LK_EXALT[p].includes(h[p]) ? "exalted (LK)" : LK_DEBIL[p].includes(h[p]) ? "debilitated (LK)" : LK_PAKKA[p].includes(h[p]) ? "in pakka ghar" : "ordinary",
      pakka_ghar: LK_PAKKA[p], soya_sleeping: LK_ASPECT[h[p]] ? !LK_ASPECT[h[p]].some(x => c.occupants(x).length) : null,
      general_remedy: LK_GENERAL[p] }));
    const rin = [];
    for (const [name, f, rem] of LK_RIN) { const who = f(h); if (who.length) rin.push({ rin: name, caused_by: who, remedy: rem }); }
    const sleepingHouses = [];
    for (let x = 1; x <= 12; x++) if (!c.occupants(x).length && !c.aspectedBy(x).length) sleepingHouses.push(x);
    return { planets: rows, rin, sleeping_houses: sleepingHouses, notes: [
      "Lal Kitab (1939-1952 editions, Pt. Roop Chand Joshi) uses houses only - signs are ignored and house 1 is always treated as Aries.",
      "Lal Kitab rules often contradict Parashari rules; when they do, the report shows both and does not merge them.",
      "Do one remedy at a time for 40-43 days; avoid remedies of a planet that is exalted in LK.",
    ] };
  }

  Object.assign(J, { yogas, doshas, jaimini, profiles, gemAdvice, mantraDaan, lalKitab, pyNums });
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
