"""Point-in-time anomaly detectors: static, rolling z-score, EWMA, and seasonal baseline."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from statistics import median
from typing import Protocol

from .model import Severity, Signal
from .series import Series

WEEK = 7 * 24 * 3600


class Detector(Protocol):
    name: str

    def detect(self, series: Series) -> list[Signal]: ...


@dataclass(frozen=True)
class Threshold:
    metric: str
    op: str  # ">" or "<"
    value: float
    severity: Severity = Severity.PAGE


@dataclass(frozen=True)
class Watch:
    """A metric to watch for deviation from an expected value."""

    metric: str
    direction: str = "both"  # "up", "down", or "both"
    min_delta: float = 0.0  # ignore deviations smaller than this absolute amount
    severity: Severity = Severity.TICKET


def _deviates(watch: Watch, value: float, expected: float, band: float) -> bool:
    delta = value - expected
    if abs(delta) <= band or abs(delta) < watch.min_delta:
        return False
    return watch.direction == "both" or (watch.direction == "up") == (delta > 0)


def _signal(name: str, watch: Watch, ts: int, value: float, expected: float, how: str) -> Signal:
    return Signal(
        ts,
        name,
        watch.metric,
        watch.severity,
        value,
        expected,
        f"{watch.metric} {value:.4g} vs expected {expected:.4g} ({how})",
    )


@dataclass
class StaticThreshold:
    rules: Sequence[Threshold]
    name: str = "static"

    def detect(self, series: Series) -> list[Signal]:
        out = []
        for rule in self.rules:
            for ts, v in zip(series.ts, series.metric(rule.metric)):
                if (v > rule.value) if rule.op == ">" else (v < rule.value):
                    out.append(
                        Signal(
                            ts,
                            self.name,
                            rule.metric,
                            rule.severity,
                            v,
                            rule.value,
                            f"{rule.metric} {v:.4g} {rule.op} {rule.value:.4g}",
                        )
                    )
        return sorted(out, key=lambda s: s.ts)


@dataclass
class RollingZScore:
    """Compare each point with the mean and standard deviation of the previous `window` points."""

    watches: Sequence[Watch]
    window: int = 60
    threshold: float = 4.0
    name: str = "zscore"

    def detect(self, series: Series) -> list[Signal]:
        out = []
        for watch in self.watches:
            values = series.metric(watch.metric)
            total = sum(values[: self.window])
            total_sq = sum(v * v for v in values[: self.window])
            for i in range(self.window, len(values)):
                mean = total / self.window
                std = math.sqrt(max(total_sq / self.window - mean * mean, 0.0))
                v = values[i]
                if _deviates(watch, v, mean, self.threshold * std):
                    z = (v - mean) / std if std else math.inf
                    out.append(_signal(self.name, watch, series.ts[i], v, mean, f"z={z:.1f}"))
                old = values[i - self.window]
                total += v - old
                total_sq += v * v - old * old
        return sorted(out, key=lambda s: s.ts)


@dataclass
class EWMA:
    """Exponentially weighted mean and variance; alert when a point is `threshold` sigmas away.

    Anomalous points do not update the baseline for up to `freeze` steps.
    Without the freeze, one outlier inflates the variance and hides a sustained shift.
    """

    watches: Sequence[Watch]
    alpha: float = 0.05
    threshold: float = 4.0
    warmup: int = 60
    freeze: int = 30
    name: str = "ewma"

    def detect(self, series: Series) -> list[Signal]:
        out = []
        for watch in self.watches:
            values = series.metric(watch.metric)
            if not values:
                continue
            mean, var, streak = values[0], 0.0, 0
            for i, v in enumerate(values):
                if i >= self.warmup and _deviates(watch, v, mean, self.threshold * math.sqrt(var)):
                    out.append(_signal(self.name, watch, series.ts[i], v, mean, f"ewma alpha={self.alpha}"))
                    streak += 1
                    if streak <= self.freeze:
                        continue
                else:
                    streak = 0
                diff = v - mean
                incr = self.alpha * diff
                mean += incr
                var = (1 - self.alpha) * (var + diff * incr)
        return sorted(out, key=lambda s: s.ts)


def rolling_median(values: Sequence[float], window: int, center: bool = False) -> list[float]:
    """Median over a trailing window, or a centered window when `center` is true."""
    if window <= 1:
        return list(values)
    out = []
    back = window // 2 if center else window - 1
    fwd = window - 1 - back
    for i in range(len(values)):
        out.append(median(values[max(0, i - back) : i + fwd + 1]))
    return out


@dataclass
class SeasonalBaseline:
    """Compare now with the same time in each of the last `weeks` weeks.

    The band is the envelope of the past weeks, widened by `tolerance`. With
    more than one week, one bad week cannot cause an "echo" alert a week later.
    """

    watches: Sequence[Watch]
    weeks: int = 1
    tolerance: float = 0.3
    smooth: int = 5
    period_s: int = WEEK
    name: str = field(default="")

    def __post_init__(self) -> None:
        self.name = self.name or f"seasonal_{self.weeks}w"

    def detect(self, series: Series) -> list[Signal]:
        lag = self.period_s // series.step
        out = []
        for watch in self.watches:
            raw = series.metric(watch.metric)
            now = rolling_median(raw, self.smooth)
            past = rolling_median(raw, self.smooth, center=True)
            for i in range(lag, len(raw)):
                base = [past[i - k * lag] for k in range(1, self.weeks + 1) if i - k * lag >= 0]
                lo, hi, v = min(base), max(base), now[i]
                low_hit = v < lo and _deviates(watch, v, lo, self.tolerance * lo)
                high_hit = v > hi and _deviates(watch, v, hi, self.tolerance * hi)
                if low_hit or high_hit:
                    out.append(
                        _signal(
                            self.name,
                            watch,
                            series.ts[i],
                            v,
                            median(base),
                            f"{len(base)}w band {lo:.4g}..{hi:.4g} +/-{self.tolerance:.0%}",
                        )
                    )
        return sorted(out, key=lambda s: s.ts)


@dataclass
class AnyOf:
    """Union of several detectors, scored as one."""

    detectors: Sequence[Detector]
    name: str = "any"

    def detect(self, series: Series) -> list[Signal]:
        return sorted((s for d in self.detectors for s in d.detect(series)), key=lambda s: s.ts)
