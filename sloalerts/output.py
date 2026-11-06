"""Notification sinks (console, JSONL) and the markdown incident summary."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from .alerts import AlertManager, Notification
from .series import iso


def format_notification(n: Notification) -> str:
    tag = f" (suppressed: {n.suppressed})" if n.suppressed else ""
    return f"{iso(n.ts)} [{str(n.severity).upper():6}] -> {n.route:6} {n.event:9} {n.group_id}: {n.summary}{tag}"


def to_console(
    notifications: Iterable[Notification], stream: TextIO = sys.stdout, include_suppressed: bool = False
) -> None:
    for n in notifications:
        if include_suppressed or not n.suppressed:
            print(format_notification(n), file=stream)


def to_jsonl(notifications: Iterable[Notification], path: str | Path) -> None:
    with open(path, "w") as fh:
        fh.writelines(json.dumps(n.to_dict()) + "\n" for n in notifications)


def _duration(start: int, end: int | None) -> str:
    if end is None:
        return "ongoing"
    minutes = (end - start) // 60
    return f"{minutes}m" if minutes < 120 else f"{minutes / 60:.1f}h"


def incident_summary(manager: AlertManager, title: str = "Incident summary") -> str:
    """Render one markdown section per incident group."""
    lines = [f"# {title}", ""]
    if not manager.groups:
        return "\n".join(lines + ["No alerts opened.", ""])
    by_group: dict[str, list[Notification]] = {}
    for n in manager.notifications:
        by_group.setdefault(n.group_id, []).append(n)
    lines += ["| Group | Opened (UTC) | Duration | Highest severity | Route | Alerts |", "|---|---|---|---|---|---|"]
    for g in manager.groups:
        top = max(a.severity for a in g.alerts)
        route = manager.policy.routes.get(top, "log") if g.notified is not None else "suppressed"
        lines.append(
            f"| {g.id} | {iso(g.opened_at)} | {_duration(g.opened_at, g.resolved_at)} "
            f"| {top} | {route} | {len(g.alerts)} |"
        )
    for g in manager.groups:
        lines += [
            "",
            f"## {g.id}: {g.service}",
            "",
            f"- Opened: {iso(g.opened_at)}",
            f"- Resolved: {iso(g.resolved_at) if g.resolved_at else 'still open at end of data'}",
            f"- Notified: {'yes, ' + str(g.notified) if g.notified is not None else 'no (suppressed)'}",
            "",
            "| Alert | Detector | Metric | Severity | Opened | Duration | Worst value | Expected | Flapping |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for a in g.alerts:
            lines.append(
                f"| {a.id} | {a.detector} | {a.metric} | {a.severity} | {iso(a.opened_at)} "
                f"| {_duration(a.opened_at, a.resolved_at)} | {a.value:.4g} | {a.expected:.4g} "
                f"| {'yes' if a.flapping else 'no'} |"
            )
        lines += ["", "Timeline:", ""]
        for n in by_group.get(g.id, []):
            tag = f" _(suppressed: {n.suppressed})_" if n.suppressed else ""
            lines.append(f"- {iso(n.ts)} `{n.event}` -> {n.route}: {n.summary}{tag}")
    return "\n".join(lines) + "\n"
