# Pre-registration (written before the full download finished and before any profession result was computed)

## Data classes
- G1: Rodden AA. G2: Rodden A or B. Others (C, DD, X, XX) excluded. Myth/historical charts excluded.
- Birth time zone must be a standard offset (sbli field "hNNe/w"); LMT records excluded.

## Test 1 - timing replication (hold-out)
Same code as the first study (run.js, unchanged mapping and metric), on G1 people NOT in the first study,
and separately on G2. Hypothesis of skill: real mean percentile > age-matched random-chart control.

## Test 2 - profession (descriptive, no dates)
Vocation -> planet, taken from the engine's own career table (careerProfile.fields):
- Mars: Military (all), Law : Police, Medical : Surgeon, Sports (all, not Sports Business)
- Sun: Politics : Heads of state, Politics : Public office, Politics : Government employee, Politics : Diplomat, Medical : Physician
- Venus: Entertainment : Actor/ Actress, Beauty (all), Entertain/Music (all), Art : Fine art artist, Entertain/Music : Dancer/ Teacher
- Mercury: Writers (all except Astrology), Entertainment : News journalist/ Anchor, Science : Mathematics/ Statistics
- Jupiter: Law : Attorney, Law : Jurist, Religion (all), Education : Teacher, Business : Banker/ Financier
A person is in a group only if all their vocation categories that map, map to ONE planet (no mixed people).
Link of planet P to career (engine rules: careerProfile): P occupies 10th from lagna, or P is 10th lord,
or P is navamsa dispositor of the 10th lord, or P occupies 10th from Moon. link = 1 if any, else 0.
Statistic per planet: share linked among people whose profession maps to P, minus share linked among
people whose profession maps to a different planet. Skill = positive difference, beyond 95% CI.
Report G1 and G2 separately; G1 is primary. No other link definitions will be tried and reported as main results.
