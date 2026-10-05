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

## Test 3 - physical features (written before any physical result was computed)
Data: AA/A/B records with "Traits : Body : Size" (height in m) and "Traits : Body : Weight" (kg). No complexion data
exists (only a race category, not used). Height is standardised within sex and birth decade (z-score), removing
sex and the secular rise in height. BMI = kg/m^2, standardised the same way.
Split: people with even md5(name) = exploration half A, odd = confirmation half B.
Primary (no tuning): Pearson r between the engine's self_appearance height score and height z, and between the
build score and BMI z, on all people. Skill = r > 0 beyond 95% CI.
Exploration: on half A only, test single classical features (lagna sign height class hrasva/sama/dirgha, lagna lord's
sign class, Moon sign class, D9 lagna class, each planet in lagna, Jupiter/Saturn/Mars aspect on lagna, lagna-lord
dignity score). Any feature with |r| p<0.05 on A is then tested on B with Bonferroni correction for the number carried
over. Only features that pass on B may change the engine.

## Test 4 - temperament (written before running)
Assertive group: Traits : Personality : Aggressive/ brash, Temper, Fiery, Courageous.
Reserved group: Shy, Passive/ Bland, Solitary/ Introvert, Private. People in both groups excluded. AA/A/B only.
Classical indicators of an assertive nature (each tested): Mars in lagna or aspecting lagna or Mars is lagna lord;
fire-sign lagna (Aries/Leo/Sagittarius); fire-sign Moon; Mars dignity score >= 3 (own/exalted/MT/great friend).
Skill = indicator more common in the assertive group than the reserved group, beyond 95% CI.
