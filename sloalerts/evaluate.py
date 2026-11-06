"""Score detectors against labeled incidents: precision, recall, and time to detect."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from statistics import median

from .alerts import Alert, AlertManager, AlertPolicy
from .detectors import Detector
from .model import Incident
from .series import Series
from .synth import INCIDENT_KINDS

WEEK = 7 * 24 * 3600


@dataclass
class KindScore:
    total: int = 0
    ttd_s: list[int] = field(default_factory=list)

    @property
    def detected(self) -> int:
        return len(self.ttd_s)

    @property
    def recall(self) -> float:
        return self.detected / self.total if self.total else 0.0

    @property
    def median_ttd_s(self) -> float | None:
        return median(self.ttd_s) if self.ttd_s else None


@dataclass
class DetectorScore:
    name: str
    alerts: int
    true_alerts: int
    weeks: float
    per_kind: dict[str, KindScore]

    @property
    def false_alerts(self) -> int:
        return self.alerts - self.true_alerts

    @property
    def precision(self) -> float | None:
        return self.true_alerts / self.alerts if self.alerts else None

    @property
    def recall(self) -> float:
        total = sum(k.total for k in self.per_kind.values())
        return sum(k.detected for k in self.per_kind.values()) / total if total else 0.0


def matches(alert: Alert, incident: Incident, grace_s: int) -> bool:
    """An alert detects an incident when it opens during the incident or within the grace period."""
    return incident.start <= alert.opened_at <= incident.end + grace_s


def score(
    name: str, alerts: Sequence[Alert], incidents: Sequence[Incident], weeks: float, grace_s: int = 3600
) -> DetectorScore:
    per_kind: dict[str, KindScore] = {}
    for inc in incidents:
        ks = per_kind.setdefault(inc.kind, KindScore())
        ks.total += 1
        hits = [a.opened_at - inc.start for a in alerts if matches(a, inc, grace_s)]
        if hits:
            ks.ttd_s.append(min(hits))
    true_alerts = sum(1 for a in alerts if any(matches(a, i, grace_s) for i in incidents))
    return DetectorScore(name, len(alerts), true_alerts, weeks, per_kind)


def evaluate(
    series: Series,
    incidents: Sequence[Incident],
    detectors: Sequence[Detector],
    policy: AlertPolicy,
    grace_s: int = 3600,
) -> list[DetectorScore]:
    weeks = len(series) * series.step / WEEK
    out = []
    for det in detectors:
        manager = AlertManager(policy, service=series.service)
        manager.run(series.ts, det.detect(series))
        out.append(score(det.name, manager.alerts, incidents, weeks, grace_s))
    return out


def fmt_duration(seconds: float) -> str:
    minutes = seconds / 60
    return f"{minutes:.0f}m" if minutes < 120 else f"{minutes / 60:.1f}h"


def comparison_table(scores: Sequence[DetectorScore]) -> str:
    """Markdown table: rows are incident kinds, columns are detectors."""
    kinds = sorted(
        {k for s in scores for k in s.per_kind},
        key=lambda k: (INCIDENT_KINDS.index(k) if k in INCIDENT_KINDS else len(INCIDENT_KINDS), k),
    )
    head = "| Incident type | " + " | ".join(s.name for s in scores) + " |"
    lines = [head, "|---|" + "---|" * len(scores)]
    for kind in kinds:
        total = scores[0].per_kind[kind].total
        cells = []
        for s in scores:
            ks = s.per_kind[kind]
            ttd = f" in {fmt_duration(ks.median_ttd_s)}" if ks.median_ttd_s is not None else ""
            cells.append(f"{ks.detected}/{ks.total}{ttd}")
        lines.append(f"| {kind} (n={total}) | " + " | ".join(cells) + " |")
    lines.append("| **Recall** | " + " | ".join(f"{s.recall:.0%}" for s in scores) + " |")
    lines.append(
        "| **Precision** | " + " | ".join("n/a" if s.precision is None else f"{s.precision:.0%}" for s in scores) + " |"
    )
    lines.append("| **False alerts / week** | " + " | ".join(f"{s.false_alerts / s.weeks:.1f}" for s in scores) + " |")
    return "\n".join(lines) + "\n"
