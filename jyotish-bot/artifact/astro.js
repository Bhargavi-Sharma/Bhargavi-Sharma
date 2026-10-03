/* Ephemeris layer: Astronomy Engine positions converted to the same sidereal frame as
   Swiss Ephemeris (Lahiri): sidereal = true-ecliptic-of-date longitude - mean ayanamsa - nutation. */
(function (root) {
  const A = root.Astronomy || (typeof require !== "undefined" ? require("astronomy-engine") : null);
  const AYAN_J2000 = { lahiri: 23.857092353708822 };
  const SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const norm = x => ((x % 360) + 360) % 360;
  const rad = Math.PI / 180;

  const jdToDate = jd => new Date((jd - 2440587.5) * 86400000);
  const dateToJd = d => d.getTime() / 86400000 + 2440587.5;
  const precession = T => (5028.796195 * T + 1.1054348 * T * T + 0.00007964 * T ** 3) / 3600;

  function ayanamsa(jd) { return AYAN_J2000.lahiri + precession((jd - 2451545) / 36525); }

  function tropicalTrue(body, t) {
    const v = A.RotateVector(A.Rotation_EQJ_ECT(t), A.GeoVector(A.Body[body], t, true));
    return A.SphereFromVector(v);
  }

  function meanNode(jd) {
    const T = (jd - 2451545) / 36525;
    return norm(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T ** 3 / 467441 - T ** 4 / 60616000);
  }

  function snapshot(jd, lat, lon) {
    const t = A.MakeTime(jdToDate(jd));
    const tilt = A.e_tilt(t);
    const off = ayanamsa(jd) + tilt.dpsi / 3600;
    const bodies = {};
    for (const p of SEVEN) {
      const s = tropicalTrue(p, t);
      const s2 = tropicalTrue(p, A.MakeTime(jdToDate(jd + 0.01)));
      const s1 = tropicalTrue(p, A.MakeTime(jdToDate(jd - 0.01)));
      const eqd = A.SphereFromVector(A.RotateVector(A.Rotation_EQJ_EQD(t), A.GeoVector(A.Body[p], t, true)));
      bodies[p] = { lon: norm(s.lon - off), lat: s.lat, speed: (((s2.lon - s1.lon + 540) % 360) - 180) / 0.02, decl: eqd.lat };
    }
    const n = meanNode(jd), n2 = meanNode(jd + 1);
    const nodeLon = norm(n - ayanamsa(jd));
    const nsp = ((n2 - n + 540) % 360) - 180;
    bodies.Rahu = { lon: nodeLon, lat: 0, speed: nsp, decl: 0 };
    bodies.Ketu = { lon: norm(nodeLon + 180), lat: 0, speed: nsp, decl: 0 };
    const snap = { jd, ayanamsa: ayanamsa(jd), bodies };
    if (lat != null && lon != null) {
      const ramc = norm(A.SiderealTime(t) * 15 + lon) * rad;
      const eps = tilt.tobl * rad, phi = lat * rad;
      const asc = Math.atan2(Math.cos(ramc), -(Math.sin(ramc) * Math.cos(eps) + Math.tan(phi) * Math.sin(eps))) / rad;
      const mc = Math.atan2(Math.sin(ramc), Math.cos(ramc) * Math.cos(eps)) / rad;
      snap.asc = norm(asc - off);
      snap.mc = norm(mc - off);
    }
    return snap;
  }

  /* Sunrise before the moment, then sunset and next sunrise: disc centre, no refraction (as the Python engine). */
  function sunEvents(jd, lat, lon) {
    const obs = new A.Observer(lat, lon, 0);
    const find = (startJd, dir) => {
      const r = A.SearchAltitude(A.Body.Sun, obs, dir, A.MakeTime(jdToDate(startJd)), 2, 0);
      return r ? dateToJd(r.date) : null;
    };
    let rise = find(jd - 1.0, +1);
    while (rise != null) {
      const nr = find(rise + 0.01, +1);
      if (nr == null || nr > jd) break;
      rise = nr;
    }
    if (rise == null || rise > jd) rise = jd - ((jd + 0.5 + lon / 360) % 1) + 0.25;
    const set = find(rise + 0.01, -1) ?? rise + 0.5;
    const nextRise = find(rise + 0.5, +1) ?? rise + 1;
    const isDay = rise <= jd && jd < set;
    const weekday = Math.floor((rise + 1.5 + lon / 360) % 7);
    const WL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
    const HO = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"];
    const idx = isDay ? Math.floor((jd - rise) / ((set - rise) / 12)) : 12 + Math.floor((jd - set) / ((nextRise - set) / 12));
    const hora = HO[(HO.indexOf(WL[weekday]) + idx) % 7];
    return { sunrise: rise, sunset: set, next_sunrise: nextRise, is_day: isDay, weekday, vara_lord: WL[weekday], hora_lord: hora };
  }

  /* Local wall-clock time in an IANA zone (or fixed offset hours) -> UTC Date. */
  function localToUtc(y, mo, d, h, mi, s, tz) {
    const guess = Date.UTC(y, mo - 1, d, h, mi, s);
    if (typeof tz === "number" || /^[+-]?\d+(\.\d+)?$/.test(String(tz))) return new Date(guess - Number(tz) * 3600000);
    const offsetAt = ms => {
      const f = new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit",
        day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" });
      const p = Object.fromEntries(f.formatToParts(new Date(ms)).map(x => [x.type, x.value]));
      return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second) - ms;
    };
    let ms = guess - offsetAt(guess);
    ms = guess - offsetAt(ms);
    return new Date(ms);
  }

  /* Sidereal longitude of one graha (fast path for transit scans). */
  function siderealLon(body, jd) {
    if (body === "Rahu" || body === "Ketu") {
      const r = norm(meanNode(jd) - ayanamsa(jd));
      return body === "Rahu" ? r : norm(r + 180);
    }
    const t = A.MakeTime(jdToDate(jd));
    return norm(tropicalTrue(body, t).lon - ayanamsa(jd) - A.e_tilt(t).dpsi / 3600);
  }

  const api = { snapshot, siderealLon, sunEvents, ayanamsa, localToUtc, jdToDate, dateToJd, norm };
  if (typeof module !== "undefined") module.exports = api; else root.Astro = api;
})(typeof window !== "undefined" ? window : globalThis);
