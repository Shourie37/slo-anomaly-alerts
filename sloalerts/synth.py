"""Deterministic synthetic metrics with daily/weekly seasonality and labeled incidents."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .model import Incident
from .series import Series

MINUTE = 60
HOUR = 3600
DAY = 24 * HOUR
WEEK = 7 * DAY
START = 1767571200  # 2026-01-05T00:00:00Z, a Monday

INCIDENT_KINDS = ("traffic_drop", "error_spike", "latency_regression", "slow_burn")
DURATIONS = {
    "traffic_drop": 60 * MINUTE,
    "error_spike": 15 * MINUTE,
    "latency_regression": 90 * MINUTE,
    "slow_burn": 16 * HOUR,
}
NOTES = {
    "traffic_drop": "requests fall 45%; errors stay near zero, so availability stays ~100%",
    "error_spike": "error rate jumps to 8%",
    "latency_regression": "p50 x2.5, p90 x4.5, p99 x4 (slow dependency)",
    "slow_burn": "error rate ramps linearly from baseline to 1.2% over 16h",
}


@dataclass
class SyntheticData:
    series: Series
    incidents: list[Incident]
    noise: list[Incident]


def _poisson(rng: random.Random, lam: float) -> int:
    if lam > 30:
        return max(0, round(rng.gauss(lam, math.sqrt(lam))))
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def _load(ts: int) -> float:
    """Traffic shape: daily peak at 15:00 UTC, trough at 03:00, weekends at 70%."""
    hour = (ts % DAY) / HOUR
    daily = 1.0 + 0.6 * math.sin(2 * math.pi * (hour - 9) / 24)
    weekend = 0.7 if ((ts - START) // DAY) % 7 >= 5 else 1.0
    return daily * weekend


def _schedule(rng: random.Random, weeks: int, per_kind: int) -> list[Incident]:
    """One incident per slot after the warm-up week, with enough quiet time after each."""
    kinds = [k for k in INCIDENT_KINDS for _ in range(per_kind)]
    rng.shuffle(kinds)
    first, last = START + WEEK, START + weeks * WEEK
    slot = (last - first) // len(kinds)
    out = []
    for i, kind in enumerate(kinds):
        dur = DURATIONS[kind]
        lo = first + i * slot + 2 * HOUR
        hi = first + (i + 1) * slot - dur - 8 * HOUR
        start = lo + rng.randrange(0, max(1, (hi - lo) // MINUTE)) * MINUTE
        out.append(Incident(f"I{i + 1:02d}", kind, start, start + dur, NOTES[kind]))
    return out


def _noise(rng: random.Random, weeks: int, busy: list[Incident]) -> list[Incident]:
    """Short benign events that should not page anyone."""
    plan = [("error_blip", 3 * MINUTE, 10), ("latency_blip", 2 * MINUTE, 10), ("traffic_surge", 40 * MINUTE, 3)]
    out: list[Incident] = []
    for kind, dur, count in plan:
        placed = 0
        while placed < count:
            start = START + rng.randrange(HOUR, weeks * WEEK - HOUR) // MINUTE * MINUTE
            clash = any(start < b.end + 2 * HOUR and start + dur > b.start - 2 * HOUR for b in busy + out)
            if not clash:
                out.append(Incident(f"N{len(out) + 1:02d}", kind, start, start + dur, "benign noise"))
                placed += 1
    return sorted(out, key=lambda n: n.start)


def generate(
    seed: int = 42, weeks: int = 4, step_s: int = MINUTE, base_rpm: float = 1200.0, per_kind: int = 3
) -> SyntheticData:
    rng = random.Random(seed)
    incidents = _schedule(rng, weeks, per_kind)
    noise = _noise(rng, weeks, incidents)
    ts_list = list(range(START, START + weeks * WEEK, step_s))
    cols: dict[str, list[float]] = {c: [] for c in ("requests", "errors", "p50_ms", "p90_ms", "p99_ms")}
    base_err = 0.0002
    for ts in ts_list:
        load = _load(ts)
        rpm = base_rpm * load * step_s / MINUTE
        err_rate = base_err
        lat = [40.0 * (1 + 0.25 * load), 90.0 * (1 + 0.3 * load), 180.0 * (1 + 0.35 * load)]
        for ev in (e for e in incidents + noise if e.start <= ts < e.end):
            frac = (ts - ev.start) / (ev.end - ev.start)
            if ev.kind == "traffic_drop":
                rpm *= 0.55
            elif ev.kind == "traffic_surge":
                rpm *= 1.35
            elif ev.kind == "error_spike":
                err_rate = 0.08
            elif ev.kind == "error_blip":
                err_rate = 0.06
            elif ev.kind == "slow_burn":
                err_rate = base_err + (0.012 - base_err) * frac
            elif ev.kind == "latency_regression":
                lat = [lat[0] * 2.5, lat[1] * 4.5, lat[2] * 4.0]
            elif ev.kind == "latency_blip":
                lat = [lat[0] * 1.5, lat[1] * 3.0, lat[2] * 8.0]
        requests = max(0, round(rng.gauss(rpm, math.sqrt(rpm) + 0.03 * rpm)))
        cols["requests"].append(float(requests))
        cols["errors"].append(float(min(requests, _poisson(rng, requests * err_rate))))
        p50 = lat[0] * rng.lognormvariate(0, 0.04)
        p90 = max(p50, lat[1] * rng.lognormvariate(0, 0.05))
        p99 = max(p90, lat[2] * rng.lognormvariate(0, 0.08))
        for name, v in (("p50_ms", p50), ("p90_ms", p90), ("p99_ms", p99)):
            cols[name].append(round(v, 2))
    series = Series(
        ts_list,
        cols["requests"],
        cols["errors"],
        cols["p50_ms"],
        cols["p90_ms"],
        cols["p99_ms"],
        service="checkout-api",
    )
    return SyntheticData(series, incidents, noise)
