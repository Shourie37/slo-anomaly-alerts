import math

import pytest

from sloalerts.burnrate import (
    DAY,
    HOUR,
    MINUTE,
    SLO,
    SRE_WINDOWS,
    BurnRateDetector,
    BurnWindow,
    budget_spent,
    burn_rate,
    burn_threshold,
    fraction_above,
    hours_to_exhaustion,
)
from sloalerts.model import Severity


def test_burn_rate_is_error_ratio_over_budget():
    assert burn_rate(1, 1000, 0.999) == pytest.approx(1.0)
    assert burn_rate(10, 1000, 0.999) == pytest.approx(10.0)
    assert burn_rate(0, 0, 0.999) == 0.0


def test_sre_workbook_thresholds():
    assert [round(w.burn, 2) for w in SRE_WINDOWS] == [14.4, 6.0, 3.0, 1.0]
    assert [w.severity for w in SRE_WINDOWS] == [Severity.PAGE, Severity.PAGE, Severity.TICKET, Severity.TICKET]
    assert burn_threshold(0.02, HOUR, 30 * DAY) == pytest.approx(14.4)


def test_budget_math_is_consistent():
    assert budget_spent(14.4, HOUR) == pytest.approx(0.02)
    assert budget_spent(1.0, 30 * DAY) == pytest.approx(1.0)
    assert hours_to_exhaustion(1.0) == pytest.approx(720)
    assert hours_to_exhaustion(14.4) == pytest.approx(50)
    assert hours_to_exhaustion(0) == math.inf


def test_fraction_above_hits_the_knots():
    assert fraction_above(100, 50, 100, 200) == pytest.approx(0.1)
    assert fraction_above(200, 50, 100, 200) == pytest.approx(0.01)
    assert fraction_above(50, 50, 100, 200) == pytest.approx(0.5)


def test_fraction_above_is_monotonic_and_clamped():
    values = [fraction_above(t, 50, 100, 200) for t in (1, 10, 75, 150, 300, 1000)]
    assert values == sorted(values, reverse=True)
    assert values[0] == 1.0
    assert 0 < values[-1] < 0.01


def test_fraction_above_handles_flat_percentiles():
    assert fraction_above(300, 100, 100, 100) == pytest.approx(0.01)
    assert fraction_above(50, 100, 100, 100) == pytest.approx(0.5)


FAST = (BurnWindow(HOUR, 5 * MINUTE, 14.4, Severity.PAGE),)


def test_detector_pages_on_a_hard_error_spike(series_factory):
    n = 120
    errors = [0.0] * 60 + [100.0] * 60  # 10% errors = burn 100 on a 99.9% SLO
    s = series_factory(n, requests=1000, errors=errors)
    sigs = BurnRateDetector([SLO("availability", 0.999)], FAST).detect(s)
    # The 1h window needs 14.4/100 of an hour of bad minutes: 9 minutes.
    assert sigs[0].ts == s.ts[60 + 8]
    assert sigs[0].severity == Severity.PAGE
    assert sigs[0].metric == "availability"


def test_short_window_stops_the_alert_after_recovery(series_factory):
    errors = [0.0] * 60 + [100.0] * 30 + [0.0] * 30
    s = series_factory(120, requests=1000, errors=errors)
    sigs = BurnRateDetector([SLO("availability", 0.999)], FAST).detect(s)
    last = max(x.ts for x in sigs)
    # The 1h window is still hot; the 5m window clears once it holds no bad minute.
    assert last == s.ts[90 + 3]


def test_blip_does_not_page(series_factory):
    errors = [0.0] * 60 + [60.0] * 3 + [0.0] * 57  # 3 minutes at 6%
    s = series_factory(120, requests=1000, errors=errors)
    assert BurnRateDetector([SLO("availability", 0.999)], FAST).detect(s) == []


def test_highest_severity_window_wins(series_factory):
    windows = (BurnWindow(HOUR, 5 * MINUTE, 14.4, Severity.PAGE), BurnWindow(HOUR, 5 * MINUTE, 1.0, Severity.TICKET))
    s = series_factory(70, requests=1000, errors=100)
    sigs = BurnRateDetector([SLO("availability", 0.999)], windows).detect(s)
    assert {x.severity for x in sigs} == {Severity.PAGE}
    assert len(sigs) == 70


def test_latency_slo_uses_slow_request_share(series_factory):
    # p90 equals the threshold, so 10% of requests are slow: burn 10 on a 99% SLO.
    s = series_factory(60, requests=1000, p50=100, p90=400, p99=900)
    slo = SLO("latency", 0.99, latency_threshold_ms=400)
    sigs = BurnRateDetector([slo], (BurnWindow(HOUR, 5 * MINUTE, 9.9, Severity.PAGE),)).detect(s)
    assert len(sigs) == 60
    assert sigs[0].value == pytest.approx(10.0)
