"""Multi-window, multi-burn-rate SLO alerts for availability and latency SLOs."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from itertools import accumulate

from .model import Severity, Signal
from .series import Series

MINUTE = 60
HOUR = 3600
DAY = 24 * HOUR


@dataclass(frozen=True)
class SLO:
    """An availability SLO, or a latency SLO when `latency_threshold_ms` is set."""

    name: str
    target: float
    period_s: int = 30 * DAY
    latency_threshold_ms: float | None = None

    @property
    def budget(self) -> float:
        return 1.0 - self.target


@dataclass(frozen=True)
class BurnWindow:
    long_s: int
    short_s: int
    burn: float
    severity: Severity


def burn_rate(bad: float, total: float, target: float) -> float:
    """How many times faster than "exactly on budget" the error budget burns."""
    if total <= 0:
        return 0.0
    return (bad / total) / (1.0 - target)


def burn_threshold(budget_fraction: float, window_s: int, period_s: int = 30 * DAY) -> float:
    """Burn rate that spends `budget_fraction` of the whole budget in `window_s`."""
    return budget_fraction * period_s / window_s


def budget_spent(burn: float, window_s: int, period_s: int = 30 * DAY) -> float:
    return burn * window_s / period_s


def hours_to_exhaustion(burn: float, period_s: int = 30 * DAY) -> float:
    return math.inf if burn <= 0 else period_s / burn / HOUR


# Google SRE Workbook, "Alerting on SLOs": 2% of budget in 1h, 5% in 6h, 10% in 1d and 3d.
SRE_WINDOWS: tuple[BurnWindow, ...] = (
    BurnWindow(HOUR, 5 * MINUTE, burn_threshold(0.02, HOUR), Severity.PAGE),
    BurnWindow(6 * HOUR, 30 * MINUTE, burn_threshold(0.05, 6 * HOUR), Severity.PAGE),
    BurnWindow(DAY, 2 * HOUR, burn_threshold(0.10, DAY), Severity.TICKET),
    BurnWindow(3 * DAY, 6 * HOUR, burn_threshold(0.10, 3 * DAY), Severity.TICKET),
)


def fraction_above(threshold_ms: float, p50: float, p90: float, p99: float) -> float:
    """Estimate the share of requests slower than `threshold_ms` from three percentiles.

    Interpolates log(tail share) linearly against log(latency) between the
    (p50, 0.5), (p90, 0.1), and (p99, 0.01) knots, and extrapolates outside them.
    """
    knots = [(max(p50, 1e-9), 0.5), (max(p90, p50, 1e-9), 0.1), (max(p99, p90, p50, 1e-9), 0.01)]
    x = math.log(max(threshold_ms, 1e-9))
    lo, hi = (knots[0], knots[1]) if x <= math.log(knots[1][0]) else (knots[1], knots[2])
    x0, x1 = math.log(lo[0]), math.log(hi[0])
    y0, y1 = math.log(lo[1]), math.log(hi[1])
    if x1 <= x0:
        return hi[1] if x >= x1 else lo[1]
    return min(1.0, math.exp(y0 + (y1 - y0) * (x - x0) / (x1 - x0)))


def bad_events(series: Series, slo: SLO) -> list[float]:
    if slo.latency_threshold_ms is None:
        return list(series.errors)
    t = slo.latency_threshold_ms
    return [
        r * fraction_above(t, a, b, c)
        for r, a, b, c in zip(series.requests, series.p50_ms, series.p90_ms, series.p99_ms)
    ]


@dataclass
class BurnRateDetector:
    """Fire when both the long and the short window burn faster than the window's threshold."""

    slos: Sequence[SLO]
    windows: Sequence[BurnWindow] = field(default_factory=lambda: SRE_WINDOWS)
    name: str = "burn_rate"

    def detect(self, series: Series) -> list[Signal]:
        out = []
        for slo in self.slos:
            pb = [0.0, *accumulate(bad_events(series, slo))]
            pt = [0.0, *accumulate(series.requests)]
            for i, ts in enumerate(series.ts):
                best = None
                for w in self.windows:
                    long_b = _window_burn(pb, pt, i, max(1, w.long_s // series.step), slo.target)
                    short_b = _window_burn(pb, pt, i, max(1, w.short_s // series.step), slo.target)
                    if long_b >= w.burn and short_b >= w.burn and (best is None or w.severity > best[0].severity):
                        best = (w, long_b, short_b)
                if best:
                    w, long_b, short_b = best
                    out.append(
                        Signal(
                            ts,
                            self.name,
                            slo.name,
                            w.severity,
                            long_b,
                            w.burn,
                            f"{slo.name} SLO {slo.target:.2%}: burn {long_b:.1f}x over "
                            f"{_dur(w.long_s)} and {short_b:.1f}x over {_dur(w.short_s)} "
                            f">= {w.burn:g}x",
                        )
                    )
        return sorted(out, key=lambda s: s.ts)


def _window_burn(bad_prefix: list[float], total_prefix: list[float], i: int, n: int, target: float) -> float:
    lo = max(0, i + 1 - n)
    return burn_rate(bad_prefix[i + 1] - bad_prefix[lo], total_prefix[i + 1] - total_prefix[lo], target)


def _dur(seconds: int) -> str:
    if seconds % DAY == 0:
        return f"{seconds // DAY}d"
    if seconds % HOUR == 0:
        return f"{seconds // HOUR}h"
    return f"{seconds // MINUTE}m"
