"""Shared value types: severity, detector signals, and labeled incidents."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import IntEnum
from pathlib import Path

from .series import iso, parse_ts


class Severity(IntEnum):
    INFO = 0
    TICKET = 1
    PAGE = 2

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def parse(cls, text: str) -> Severity:
        return cls[text.strip().upper()]


@dataclass(frozen=True)
class Signal:
    """One detector says one metric looks wrong at one timestamp."""

    ts: int
    detector: str
    metric: str
    severity: Severity
    value: float
    expected: float
    message: str = ""


@dataclass(frozen=True)
class Incident:
    """A ground-truth interval [start, end) with a kind such as traffic_drop."""

    id: str
    kind: str
    start: int
    end: int
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {**asdict(self), "start_iso": iso(self.start), "end_iso": iso(self.end)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Incident:
        return cls(
            id=str(data["id"]),
            kind=str(data["kind"]),
            start=parse_ts(data["start"]),
            end=parse_ts(data["end"]),
            note=str(data.get("note", "")),
        )


def save_labels(path: str | Path, incidents: list[Incident], noise: list[Incident] = ()) -> None:
    payload = {"incidents": [i.to_dict() for i in incidents], "noise": [n.to_dict() for n in noise]}
    Path(path).write_text(json.dumps(payload, indent=2) + "\n")


def load_labels(path: str | Path) -> list[Incident]:
    data = json.loads(Path(path).read_text())
    items = data["incidents"] if isinstance(data, dict) else data
    return [Incident.from_dict(item) for item in items]
