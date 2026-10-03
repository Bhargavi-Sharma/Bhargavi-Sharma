import json
from datetime import datetime, timedelta, timezone

import pytest

from jyotish import ashtakavarga, dasha, dossier, functional, shadbala, timing
from jyotish.chart import BirthData, Chart
from jyotish.constants import DASHA_YEARS
from jyotish.dignity import dignity
from jyotish.vargas import varga_sign

DELHI = BirthData("Test", datetime(1990, 5, 15, 10, 30), "Asia/Kolkata", 28.6139, 77.209, "Delhi", "M")


@pytest.fixture(scope="module")
def chart():
    return Chart(DELHI)


def test_positions_sane(chart):
    assert chart.sign["Sun"] == 1  # sidereal Sun enters Taurus around 14-15 May
    assert chart.sun["vara_lord"] == "Mars"  # 15 May 1990 was a Tuesday
    assert abs((chart.lon["Rahu"] - chart.lon["Ketu"]) % 360 - 180) < 1e-6


def test_ashtakavarga_totals(chart):
    av = ashtakavarga.compute(chart.sign, chart.lagna)
    assert {p: sum(r) for p, r in av["bav"].items()} == ashtakavarga.BAV_TOTALS
    assert sum(av["sav"]) == 337


@pytest.mark.parametrize("lon,d,expected", [
    (0.0, 9, 0), (3.34, 9, 1), (30.0, 9, 9), (60.0, 9, 6), (359.9, 9, 11),
    (2.0, 30, 0), (7.0, 30, 10), (32.0, 30, 1), (40.0, 30, 5),
    (35.0, 10, 10), (32.0, 10, 9), (5.0, 2, 4), (35.0, 2, 3), (12.0, 3, 4), (31.0, 7, 7), (0.2, 60, 0),
])
def test_vargas(lon, d, expected):
    assert varga_sign(lon, d) == expected


def test_dignity_edges():
    signs = {p: 0 for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")}
    assert dignity("Sun", 0, 10, signs) == "Exalted"
    assert dignity("Moon", 1, 2, signs) == "Exalted"
    assert dignity("Moon", 1, 10, signs) == "Moolatrikona"
    assert dignity("Mercury", 5, 17, signs) == "Moolatrikona"
    assert dignity("Mercury", 5, 25, signs) == "Own"
    assert dignity("Saturn", 0, 20, signs) == "Debilitated"


def test_dasha_cycle(chart):
    v = dasha.vimshottari(chart.lon["Moon"], chart.utc)
    first_full = v["mahadashas"][1]
    nine = v["mahadashas"][1:10]
    span = (nine[-1]["end"] - nine[0]["start"]).days / 365.25
    assert abs(span - sum(DASHA_YEARS.values())) < 0.01
    ads = dasha.antardashas(first_full)
    assert ads[0]["lord"] == first_full["lord"] and abs((ads[-1]["end"] - first_full["end"]).total_seconds()) < 1
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    run = dasha.running(v, now)
    assert run["md"]["start"] <= now < run["md"]["end"]


def test_functional_yogakaraka():
    # Libra lagna: Saturn owns 4 and 5 -> yogakaraka
    for hour in range(24):
        c = Chart(BirthData("x", datetime(2000, 1, 1, hour, 0), 5.5, 28.6, 77.2))
        if c.lagna == 6:
            assert functional.functional_nature(c)["yogakarakas"] == ["Saturn"]
            return
    pytest.fail("no Libra lagna found in the day")


def test_shadbala_ranges(chart):
    s = shadbala.compute(chart)
    for p, v in s["planets"].items():
        assert 2 < v["rupas"] < 15, (p, v["rupas"])


def test_event_windows_and_rectification(chart):
    w = timing.event_windows(chart, "marriage", datetime(2012, 1, 1, tzinfo=timezone.utc),
                             datetime(2030, 1, 1, tzinfo=timezone.utc))
    assert w["windows"] and all("confidence" in x for x in w["windows"])
    r = timing.rectify_by_events(Chart, DELHI, [{"area": "career", "date": "2014-06-01"}], minutes=10, step=5)
    assert len(r) == 5


def test_dossier_serialises():
    d = dossier.build(DELHI, now=datetime(2026, 10, 3, tzinfo=timezone.utc))
    s = json.dumps(d, default=dossier.serialise, ensure_ascii=False)
    assert "life_areas" in d and "profiles" in d and len(s) > 50_000
    assert d["jaimini"]["longevity"]["category"] in ("Short (Alpa)", "Medium (Madhya)", "Long (Purna)")


def test_bot_tools_offline(chart):
    from jyotish.bot import run_tool
    out = json.loads(run_tool(chart, "get_dasha_at", {"date": "2020-01-01"}))
    assert set(out) == {"md", "ad", "pd"}
    pd = json.loads(run_tool(chart, "get_pratyantars", {"mahadasha": out["md"]["lord"], "antardasha": out["ad"]["lord"],
                                                        "occurrence_year": 2020}))
    assert len(pd) == 9
