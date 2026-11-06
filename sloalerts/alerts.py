"""Alert manager: hysteresis, dedup, grouping, flapping suppression, maintenance, and routing."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from .model import Severity, Signal
from .series import iso

DEFAULT_ROUTES: Mapping[Severity, str] = {Severity.PAGE: "pager", Severity.TICKET: "ticket", Severity.INFO: "log"}

Key = tuple[str, str, str]  # (service, detector, metric)


@dataclass(frozen=True)
class AlertPolicy:
    pending_s: int = 120  # the condition must hold this long before the alert opens
    resolve_s: int = 900  # quiet time before the alert resolves
    flap_window_s: int = 3600
    flap_max_opens: int = 3  # this many opens inside the flap window marks the alert as flapping
    group_by: tuple[str, ...] = ("service",)
    routes: Mapping[Severity, str] = field(default_factory=lambda: dict(DEFAULT_ROUTES))


@dataclass(frozen=True)
class MaintenanceWindow:
    start: int
    end: int
    service: str | None = None
    reason: str = "maintenance"

    def covers(self, ts: int, service: str) -> bool:
        return self.start <= ts < self.end and self.service in (None, service)


@dataclass
class Alert:
    id: str
    service: str
    detector: str
    metric: str
    severity: Severity
    first_seen: int
    opened_at: int
    last_seen: int
    value: float
    expected: float
    message: str
    resolved_at: int | None = None
    flapping: bool = False
    group_id: str = ""

    @property
    def key(self) -> Key:
        return (self.service, self.detector, self.metric)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "service": self.service,
            "detector": self.detector,
            "metric": self.metric,
            "severity": str(self.severity),
            "opened_at": iso(self.opened_at),
            "resolved_at": iso(self.resolved_at) if self.resolved_at else None,
            "value": self.value,
            "expected": self.expected,
            "message": self.message,
            "flapping": self.flapping,
            "group": self.group_id,
        }


@dataclass
class Group:
    id: str
    key: tuple[str, ...]
    service: str
    opened_at: int
    alerts: list[Alert] = field(default_factory=list)
    resolved_at: int | None = None
    notified: Severity | None = None
    suppressed_at: Severity | None = None

    def active(self) -> list[Alert]:
        return [a for a in self.alerts if a.resolved_at is None]

    def severity(self) -> Severity | None:
        live = [a.severity for a in self.active() if not a.flapping]
        return max(live) if live else None


@dataclass(frozen=True)
class Notification:
    ts: int
    event: str  # open, escalate, update, resolve, flapping
    group_id: str
    severity: Severity
    route: str
    summary: str
    alert_ids: tuple[str, ...]
    suppressed: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "ts": iso(self.ts),
            "event": self.event,
            "group": self.group_id,
            "severity": str(self.severity),
            "route": self.route,
            "summary": self.summary,
            "alerts": list(self.alert_ids),
            "suppressed": self.suppressed,
        }


class AlertManager:
    """Turn per-step detector signals into alerts, incident groups, and notifications."""

    def __init__(
        self, policy: AlertPolicy | None = None, maintenance: Sequence[MaintenanceWindow] = (), service: str = "demo"
    ) -> None:
        self.policy = policy or AlertPolicy()
        self.maintenance = list(maintenance)
        self.service = service
        self.alerts: list[Alert] = []
        self.groups: list[Group] = []
        self.notifications: list[Notification] = []
        self._pending: dict[Key, int] = {}
        self._firing: dict[Key, Alert] = {}
        self._opens: dict[Key, deque[int]] = defaultdict(deque)
        self._flapping: dict[Key, bool] = {}
        self._open_groups: dict[tuple[str, ...], Group] = {}

    def run(self, timestamps: Iterable[int], signals: Iterable[Signal]) -> list[Notification]:
        by_ts: dict[int, list[Signal]] = defaultdict(list)
        for s in signals:
            by_ts[s.ts].append(s)
        for ts in timestamps:
            self.step(ts, by_ts.get(ts, ()))
        return self.notifications

    def step(self, ts: int, signals: Iterable[Signal]) -> None:
        firing = self._dedup(signals)
        for key, sig in firing.items():
            self._on_fire(ts, key, sig)
        for key in [k for k in self._pending if k not in firing]:
            del self._pending[key]
        for key, alert in list(self._firing.items()):
            if key not in firing and ts - alert.last_seen >= self.policy.resolve_s:
                self._resolve(ts, alert)
        self._reconcile(ts)

    def _dedup(self, signals: Iterable[Signal]) -> dict[Key, Signal]:
        strongest: dict[Key, Signal] = {}
        for s in signals:
            key = (self.service, s.detector, s.metric)
            if key not in strongest or s.severity > strongest[key].severity:
                strongest[key] = s
        return strongest

    def _on_fire(self, ts: int, key: Key, sig: Signal) -> None:
        alert = self._firing.get(key)
        if alert:
            alert.last_seen = ts
            if sig.severity > alert.severity:
                alert.severity, alert.message = sig.severity, sig.message
            if abs(sig.value - sig.expected) > abs(alert.value - alert.expected):
                alert.value, alert.expected = sig.value, sig.expected
            return
        since = self._pending.setdefault(key, ts)
        if ts - since >= self.policy.pending_s:
            del self._pending[key]
            self._open(ts, key, sig, since)

    def _open(self, ts: int, key: Key, sig: Signal, since: int) -> None:
        alert = Alert(
            f"A{len(self.alerts) + 1}",
            key[0],
            key[1],
            key[2],
            sig.severity,
            since,
            ts,
            ts,
            sig.value,
            sig.expected,
            sig.message,
        )
        opens = self._opens[key]
        opens.append(ts)
        while opens and opens[0] <= ts - self.policy.flap_window_s:
            opens.popleft()
        was_flapping = self._flapping.get(key, False)
        alert.flapping = self._flapping[key] = len(opens) >= self.policy.flap_max_opens
        self.alerts.append(alert)
        self._firing[key] = alert

        fields = {"service": alert.service, "detector": alert.detector, "metric": alert.metric}
        gkey = tuple(fields[f] for f in self.policy.group_by)
        group = self._open_groups.get(gkey)
        joined = group is not None
        if group is None:
            group = Group(f"G{len(self.groups) + 1}", gkey, alert.service, ts)
            self.groups.append(group)
            self._open_groups[gkey] = group
        group.alerts.append(alert)
        alert.group_id = group.id

        if alert.flapping and not was_flapping:
            self._notify(
                ts,
                "flapping",
                group,
                Severity.INFO,
                [alert],
                f"{alert.detector}/{alert.metric} opened {len(opens)} times in "
                f"{self.policy.flap_window_s // 60}m; notifications held until it is stable",
            )
        elif joined and group.notified is not None and not alert.flapping:
            self._notify(ts, "update", group, Severity.INFO, [alert], f"joined: {alert.message}")

    def _resolve(self, ts: int, alert: Alert) -> None:
        alert.resolved_at = ts
        del self._firing[alert.key]
        group = next(g for g in self._open_groups.values() if g.id == alert.group_id)
        if group.active():
            return
        group.resolved_at = ts
        del self._open_groups[group.key]
        if group.notified is not None:
            self._notify(
                ts, "resolve", group, group.notified, group.alerts, f"all {len(group.alerts)} alert(s) resolved"
            )

    def _reconcile(self, ts: int) -> None:
        for group in self._open_groups.values():
            sev = group.severity()
            if sev is None or (group.notified is not None and sev <= group.notified):
                continue
            window = self._maintenance(ts, group.service)
            if window:
                if group.suppressed_at is None or sev > group.suppressed_at:
                    group.suppressed_at = sev
                    self._notify(
                        ts, "open", group, sev, group.active(), self._headline(group), suppressed=window.reason
                    )
                continue
            event = "open" if group.notified is None else "escalate"
            group.notified = sev
            self._notify(ts, event, group, sev, group.active(), self._headline(group))

    def _maintenance(self, ts: int, service: str) -> MaintenanceWindow | None:
        return next((w for w in self.maintenance if w.covers(ts, service)), None)

    def _headline(self, group: Group) -> str:
        top = max((a for a in group.active() if not a.flapping), key=lambda a: a.severity)
        extra = len(group.active()) - 1
        return f"{group.service}: {top.message}" + (f" (+{extra} related)" if extra > 0 else "")

    def _notify(
        self,
        ts: int,
        event: str,
        group: Group,
        sev: Severity,
        alerts: Sequence[Alert],
        summary: str,
        suppressed: str | None = None,
    ) -> None:
        if suppressed is None and event in ("resolve", "update"):
            window = self._maintenance(ts, group.service)
            suppressed = window.reason if window else None
        route = self.policy.routes.get(sev, "log")
        self.notifications.append(
            Notification(ts, event, group.id, sev, route, summary, tuple(a.id for a in alerts), suppressed)
        )
