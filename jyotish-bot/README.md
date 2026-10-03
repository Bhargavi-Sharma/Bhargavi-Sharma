# Jyotish Bot

A Vedic astrology engine plus an AI astrologer. The engine computes **every** factor first: positions,
vargas, dignities, aspects, yogas *with their cancellations*, doshas *with their exceptions*, shadbala,
ashtakavarga, dashas, transits, timing windows and remedies. Then Claude reads that full report and
answers your questions from it. Because the AI reasons over one fixed, complete set of facts, it
doesn't flip from "A" to "C" when you ask again.

## Run it

```bash
cd jyotish-bot
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # from console.anthropic.com; needed only for the chat tab
uvicorn app:app --port 8000
```

Open http://localhost:8000, enter birth date, exact time and place, and press **Generate kundali**.
Every tab except Chat works without an API key.

Tests: `pip install -r requirements-dev.txt && python -m pytest -q`

## What it computes

| Area | Module | Basis |
|---|---|---|
| Planet positions, lagna, sunrise, hora | `ephemeris.py` | Swiss Ephemeris (Moshier model), Lahiri ayanamsa by default |
| 16 vargas: D1 D2 D3 D4 D7 D9 D10 D12 D16 D20 D24 D27 D30 D40 D45 D60 | `vargas.py` | BPHS ch.6-7 |
| Dignity: exaltation, debilitation, moolatrikona, own, 5-fold friendship; avasthas | `dignity.py` | BPHS ch.3, ch.45 |
| Graha drishti, conjunctions, exchanges, bhava chalit | `chart.py` | BPHS ch.26 |
| Functional benefic/malefic, yogakaraka, maraka, badhaka | `functional.py` | BPHS ch.34 |
| Combustion, retrogression, planetary war, gandanta | `functional.py`, `shadbala.py` | Surya Siddhanta; BPHS |
| Shadbala (all six balas) + ishta/kashta | `shadbala.py` | BPHS ch.27 |
| Ashtakavarga (BAV + SAV) | `ashtakavarga.py` | BPHS ch.66+ (totals self-check: 337) |
| Yogas: Mahapurusha, Gajakesari, lunar/solar yogas, Raja, Dhana, Viparita, Parivartana, Neecha Bhanga, Kemadruma, Nabhasa... each with cancellations | `yogas.py` | BPHS, Brihat Jataka, Phaladeepika, Saravali, Jataka Parijata |
| Doshas: Mangal, Kaal Sarp, Pitru, Grahan, Guru Chandal, Gandmool... each with cancellations and how classical it is | `doshas.py` | see per-dosha notes |
| Vimshottari MD / AD / PD | `dasha.py` | BPHS ch.46 |
| Gochar with vedha, Sade Sati / Dhaiya, double transit | `transits.py` | Phaladeepika ch.26; K.N. Rao's double transit |
| Life areas: promise + dated windows | `timing.py` | dasha significators + double transit + ashtakavarga |
| Spouse description, children, career type, mind | `profiles.py` | BPHS ch.3 (planet looks), Kalapurusha, Phaladeepika |
| Jaimini: chara karakas, arudha padas, karakamsha, longevity compartment | `jaimini.py` | Jaimini Sutras |
| Gemstones (with finger/enemy-gem conflicts and degree cautions), mantra/daan, Lal Kitab (pakka ghar, soya, rin) | `remedies.py` | Parashari practice; Lal Kitab 1952 |
| Birth-time sensitivity and event-based rectification | `timing.py` | |

## How accuracy and consistency are handled

* **All factors, every time.** The dossier contains every strength and weakness per planet and per
  life area. The AI is told to read all of them, apply every listed exception, and end each answer
  with the factors it checked.
* **Multiple confirmation for dates.** A window is "high" confidence only when the dasha lords
  signify the area **and** Jupiter and Saturn both influence the house or its lord by transit. Dasha
  alone is "low".
* **No flip-flopping.** The AI changes an answer only if you point to a factor it missed or give new
  information, such as a corrected birth time or a real past event.
* **Where the texts disagree, it says so.** See `variants.py`: ayanamsa, mean vs true node, node
  aspects and exaltation, combustion orbs, dasha year length, 7 vs 8 chara karakas, planetary-war
  winner, Kaal Sarp's non-classical status. The default is used and the alternatives are reported.
* **Birth time matters.** The "Birth time" tab shows how many minutes each conclusion survives. D9 can
  change within minutes and D60 within a minute or two. Give dated past events in chat to rectify.
* **Honest by design.** Difficult results are stated plainly. Health-risk periods are dated.
  Longevity is given as a classical compartment (short/medium/long). There is no death date, because
  BPHS ch.44 itself calls longevity the least reliable judgement.

## Known approximations

* Shadbala: chesta bala for Mars-Saturn uses motion categories from current speed. Abda/masa lords
  use a Kali-epoch day count. Yuddha bala is simplified. All of this is listed in the report.
* Citations are at chapter level (BPHS chapters follow the Santhanam edition numbering). No verse
  numbers are invented.
* Lal Kitab house-specific remedies are left to the AI layer, which is told to label them as Lal
  Kitab and not merge them with Parashari rules.
* Astrology is a traditional interpretive system and has not been scientifically validated. Use it
  as a lens, not for medical, legal or financial decisions.

## Browser version (Claude artifact)

`artifact/` is a JavaScript port of the same engine that runs entirely in the browser, published as
a Claude artifact. Nothing to install, and the chat runs on the viewer's own Claude plan (no API key).

* `astro.js` uses Astronomy Engine positions, converted to the same Lahiri sidereal frame as Swiss
  Ephemeris. They match the Python engine within ~15 arcseconds for planets and ~5 for the Moon.
* `engine-core.js`, `engine-rules.js`, `engine-time.js` port the Python modules one to one. On random
  charts the JS and Python reports agree on every sign, nakshatra, dasha, yoga, dosha and promise.
  The exception is a planet sitting within a few arcseconds of a pada boundary; the report flags
  those planets.
* `cities.js` embeds coordinates for ~450 cities, because artifacts cannot call geocoding services.
* `python build.py` writes `dist/` (JS escaped to ASCII) for publishing.
