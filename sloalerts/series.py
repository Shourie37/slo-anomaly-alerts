"""Time-series container and CSV/JSON loaders."""

from __future__ import annotations

import csv
import json
from bisect import bisect_left
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

COLUMNS = ("ts", "requests", "errors", "p50_ms", "p90_ms", "p99_ms")
METRICS = ("requests", "errors", "error_rate", "p50_ms", "p90_ms", "p99_ms")
_ALIASES = {"timestamp": "ts", "time": "ts", "p50": "p50_ms", "p90": "p90_ms", "p99": "p99_ms"}


def parse_ts(value: object) -> int:
    """Return epoch seconds for an int, a float, a digit string, or an ISO 8601 string."""
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip()
    if text.lstrip("-").isdigit():
        return int(text)
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return int(parsed.timestamp())


def iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Series:
    """One service's metrics on a regular time grid."""

    ts: list[int]
    requests: list[float]
    errors: list[float]
    p50_ms: list[float]
    p90_ms: list[float]
    p99_ms: list[float]
    service: str = "demo"

    def __post_init__(self) -> None:
        n = len(self.ts)
        for name in COLUMNS[1:]:
            if len(getattr(self, name)) != n:
                raise ValueError(f"column {name} has {len(getattr(self, name))} values, expected {n}")
        steps = {b - a for a, b in pairwise(self.ts)}
        if len(steps) > 1 or any(s <= 0 for s in steps):
            raise ValueError("timestamps must be increasing on a regular interval")

    def __len__(self) -> int:
        return len(self.ts)

    @property
    def step(self) -> int:
        return self.ts[1] - self.ts[0] if len(self.ts) > 1 else 60

    def metric(self, name: str) -> list[float]:
        if name == "error_rate":
            return [e / r if r > 0 else 0.0 for e, r in zip(self.errors, self.requests)]
        if name in COLUMNS[1:]:
            return getattr(self, name)
        raise KeyError(f"unknown metric {name!r}; choose from {', '.join(METRICS)}")

    def index_of(self, ts: int) -> int:
        return bisect_left(self.ts, ts)

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, object]], service: str = "demo") -> Series:
        parsed = []
        for row in rows:
            norm = {_ALIASES.get(k.strip().lower(), k.strip().lower()): v for k, v in row.items()}
            missing = [c for c in COLUMNS if c not in norm]
            if missing:
                raise ValueError(f"row is missing columns: {', '.join(missing)}")
            parsed.append((parse_ts(norm["ts"]), *(float(norm[c]) for c in COLUMNS[1:])))
        parsed.sort()
        cols = list(zip(*parsed)) if parsed else [[] for _ in COLUMNS]
        return cls(list(cols[0]), *(list(c) for c in cols[1:]), service=service)

    def rows(self) -> Iterable[dict[str, object]]:
        for i, ts in enumerate(self.ts):
            yield {"ts": ts, **{c: getattr(self, c)[i] for c in COLUMNS[1:]}}


def load_series(path: str | Path, service: str | None = None) -> Series:
    """Load a CSV file, a JSON array, a JSON object with "points", or JSON Lines."""
    path = Path(path)
    name = service or path.stem
    text = path.read_text()
    if path.suffix == ".csv":
        return Series.from_rows(csv.DictReader(text.splitlines()), service=name)
    if path.suffix == ".jsonl":
        return Series.from_rows((json.loads(line) for line in text.splitlines() if line.strip()), service=name)
    data = json.loads(text)
    if isinstance(data, dict):
        name = service or str(data.get("service", name))
        data = data["points"]
    return Series.from_rows(data, service=name)


def save_csv(series: Series, path: str | Path) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in series.rows():
            writer.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()})
