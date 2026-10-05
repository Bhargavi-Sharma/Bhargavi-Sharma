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
