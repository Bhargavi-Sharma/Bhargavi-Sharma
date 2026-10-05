# Celebrity timing study

Does the engine's event timing (Vimshottari significators + Jupiter/Saturn double transit + ashtakavarga,
`eventWindows` in `artifact/engine-time.js`) find real events better than chance?

Data: Astro-Databank (astro.com) records in the Oscar, Nobel, Grammy, Emmy, Olympics, sports championship,
knighted, Pulitzer and Tony categories, kept only if Rodden rating AA (birth certificate / record),
time zone given as an offset, and the event date has at least a month. Raw data is not committed
(copyright Astrodienst); `fetch.py` downloads it, `parse.py` filters it.

Design (fixed before any scores were seen):
- Event categories mapped to life areas by name (`MAP` in `run.js`).
- Metric: percentile rank of the event's month among all months scanned for that area
  (from a minimum age to 85 or death). 50 = chance. Also: share of events inside the top-8 named windows.
- Control: the same event placed at the same age in a different, randomly chosen person's chart.
  This removes age effects (e.g. marriages cluster in the 20s).

Run: `python3 fetch.py && python3 parse.py && node run.js 0 2800 && python3 stats.py`
(set `ASTRONOMY_ENGINE` to the astronomy-engine package path).

Result (see results.txt): 3,382 events from 1,580 people. Real 47.7 vs control 48.9
(difference -1.1 ± 1.3); 8.0% of real events inside a named window vs 8.4% for the control.
No area shows a difference that survives the number of areas tested.

## Round 2 (full database, pre-registered in PREREG.md)
Full Astro-Databank download (`fetch_all.py`, 83,472 pages) -> `parse_all.py`: 35,930 usable AA (G1) and
15,927 A/B (G2) records.
- Timing hold-out (people not in round 1, seeded random sample): G1 4,244 events / 2,727 people:
  real 48.2 vs control 49.4 (-1.2 ± 1.2). G2 2,757 events / 1,559 people: 49.1 vs 48.6 (+0.5 ± 1.5).
  (`timing_replication.txt`)
- Profession test (no dates): 22,398 G1 people. For each profession's planet, share with that planet
  linked to the 10th house vs people in other professions: Mars -1.1, Sun -0.4, Venus -1.1, Mercury +0.8,
  Jupiter -1.0 points (all within ±2.5). G2 the same. (`prof_results.txt`)

## Mythological charts (G4, kept separate, not evidence)
`myth.js` / `myth2.js`: Rama (Bhatnagar, 10 Jan 5115 BCE) and Krishna (20 Jul 3228 BCE Julian), both
Rodden XX. Event ages from the texts, scored by year. Rama 68 (7 events, but 3 are the same moment at
age 25), Krishna 39. Both dates were reconstructed from the same texts the events come from, and the
ephemeris is not reliable 5,000-7,000 years back, so this cannot test anything. Sita and Ravana have no
proposed birth data in Astro-Databank.
