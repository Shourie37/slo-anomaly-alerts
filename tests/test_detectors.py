from sloalerts.detectors import (
    EWMA,
    AnyOf,
    RollingZScore,
    SeasonalBaseline,
    StaticThreshold,
    Threshold,
    Watch,
    rolling_median,
)
from sloalerts.model import Severity


def noisy(n: int, level: float = 1000.0) -> list[float]:
    return [level + (5 if i % 2 else -5) for i in range(n)]


def test_static_threshold_fires_only_past_the_limit(series_factory):
    s = series_factory(4, requests=[100, 100, 100, 100], errors=[0, 6, 4, 10])
    det = StaticThreshold([Threshold("error_rate", ">", 0.05, Severity.PAGE)])
    sigs = det.detect(s)
    assert [x.ts for x in sigs] == [s.ts[1], s.ts[3]]
    assert all(x.severity == Severity.PAGE for x in sigs)


def test_static_threshold_misses_a_drop_above_the_floor(series_factory):
    s = series_factory(4, requests=[1000, 1000, 550, 550])
    assert StaticThreshold([Threshold("requests", "<", 100)]).detect(s) == []


def test_zscore_catches_a_step_down_and_ignores_noise(series_factory):
    values = noisy(80) + [550.0] * 5
    s = series_factory(len(values), requests=values)
    sigs = RollingZScore([Watch("requests")], window=60, threshold=4).detect(s)
    assert sigs[0].ts == s.ts[80]
    assert all(x.ts >= s.ts[80] for x in sigs)


def test_zscore_respects_direction(series_factory):
    values = noisy(80) + [550.0] * 5
    s = series_factory(len(values), requests=values)
    assert RollingZScore([Watch("requests", direction="up")], window=60).detect(s) == []


def test_zscore_min_delta_filters_tiny_moves(series_factory):
    values = [0.0] * 70 + [0.002]
    s = series_factory(len(values), requests=1000, errors=[v * 1000 for v in values])
    assert RollingZScore([Watch("error_rate", "up", min_delta=0.01)], window=60).detect(s) == []
    assert len(RollingZScore([Watch("error_rate", "up")], window=60).detect(s)) == 1


def test_ewma_holds_a_sustained_shift_with_freeze(series_factory):
    values = noisy(100) + [550.0] * 20
    s = series_factory(len(values), requests=values)
    sigs = EWMA([Watch("requests")], alpha=0.05, threshold=4, warmup=30, freeze=30).detect(s)
    assert len(sigs) == 20


def test_ewma_without_freeze_masks_the_shift(series_factory):
    values = noisy(100) + [550.0] * 20
    s = series_factory(len(values), requests=values)
    sigs = EWMA([Watch("requests")], alpha=0.05, threshold=4, warmup=30, freeze=0).detect(s)
    assert 0 < len(sigs) < 5


def test_rolling_median_trailing_and_centered():
    assert rolling_median([1, 9, 1, 1, 1], 3) == [1, 5, 1, 1, 1]
    assert rolling_median([1, 9, 1, 1, 1], 3, center=True) == [5, 1, 1, 1, 1]


def test_seasonal_compares_with_last_week(series_factory):
    period = 10 * 60  # a 10-step "week" keeps the test small
    week1 = [1000.0] * 10
    week2 = [1000.0] * 5 + [500.0] * 5
    s = series_factory(20, requests=week1 + week2)
    det = SeasonalBaseline([Watch("requests")], weeks=1, tolerance=0.3, smooth=1, period_s=period)
    assert [x.ts for x in det.detect(s)] == s.ts[15:]


def test_seasonal_follows_the_daily_shape(series_factory):
    shape = [500.0, 1000.0, 1500.0, 1000.0, 500.0] * 2
    s = series_factory(20, requests=shape + shape)
    det = SeasonalBaseline([Watch("requests")], weeks=1, smooth=1, period_s=600)
    assert det.detect(s) == []


def test_two_week_envelope_suppresses_the_echo(series_factory):
    normal, bad = [1000.0] * 10, [400.0] * 10
    s = series_factory(30, requests=normal + bad + normal)  # week 3 is normal again
    one = SeasonalBaseline([Watch("requests")], weeks=1, smooth=1, period_s=600)
    two = SeasonalBaseline([Watch("requests")], weeks=2, smooth=1, period_s=600)
    assert any(x.ts >= s.ts[20] for x in one.detect(s))  # echo of week 2
    assert all(x.ts < s.ts[20] for x in two.detect(s))


def test_any_of_merges_signals(series_factory):
    s = series_factory(3, requests=[100, 100, 100], errors=[0, 10, 0], p99=[200, 200, 2000])
    det = AnyOf(
        [
            StaticThreshold([Threshold("error_rate", ">", 0.05)]),
            StaticThreshold([Threshold("p99_ms", ">", 1000)], name="lat"),
        ]
    )
    assert [(x.detector, x.ts) for x in det.detect(s)] == [("static", s.ts[1]), ("lat", s.ts[2])]
