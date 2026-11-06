"""Command line: generate, eval, detect."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .alerts import AlertManager, MaintenanceWindow
from .evaluate import comparison_table, evaluate
from .model import load_labels, save_labels
from .output import incident_summary, to_console, to_jsonl
from .presets import DEFAULT_POLICY, default_detectors, detector_by_name
from .series import load_series, parse_ts, save_csv
from .synth import generate


def _generate(args: argparse.Namespace) -> int:
    data = generate(seed=args.seed, weeks=args.weeks)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    save_csv(data.series, out / "metrics.csv")
    save_labels(out / "labels.json", data.incidents, data.noise)
    print(f"wrote {len(data.series)} points, {len(data.incidents)} incidents, {len(data.noise)} noise events to {out}/")
    return 0


def _eval(args: argparse.Namespace) -> int:
    started = time.perf_counter()
    if args.metrics:
        if not args.labels:
            raise SystemExit("--labels is required with --metrics")
        series, incidents = load_series(args.metrics), load_labels(args.labels)
        source = args.metrics
    else:
        data = generate(seed=args.seed, weeks=args.weeks)
        series, incidents = data.series, data.incidents
        source = f"synthetic data, seed={args.seed}, weeks={args.weeks}"
    scores = evaluate(series, incidents, default_detectors(), DEFAULT_POLICY, grace_s=args.grace_min * 60)
    table = comparison_table(scores)
    print(f"Evaluation on {source}: {len(series)} points, {len(incidents)} incidents\n")
    print(table)
    print("Cells: incidents detected / total, and median time to detect.")
    print(f"Done in {time.perf_counter() - started:.1f}s.")
    if args.markdown:
        Path(args.markdown).write_text(f"Evaluation on {source}.\n\n{table}")
    return 0


def _maintenance(spec: str) -> MaintenanceWindow:
    start, _, end = spec.partition(",")
    if not end:
        raise SystemExit(f"--maintenance needs START,END, got {spec!r}")
    return MaintenanceWindow(parse_ts(start), parse_ts(end))


def _detect(args: argparse.Namespace) -> int:
    series = load_series(args.metrics, service=args.service)
    manager = AlertManager(DEFAULT_POLICY, [_maintenance(m) for m in args.maintenance], service=series.service)
    signals = [s for d in detector_by_name(args.detectors.split(",")) for s in d.detect(series)]
    notifications = manager.run(series.ts, signals)
    if not args.quiet:
        to_console(notifications, sys.stdout, include_suppressed=True)
    if args.jsonl:
        to_jsonl(notifications, args.jsonl)
    if args.summary:
        Path(args.summary).write_text(incident_summary(manager, f"Incident summary: {series.service}"))
    print(
        f"{len(manager.alerts)} alerts in {len(manager.groups)} groups, "
        f"{sum(1 for n in notifications if n.route == 'pager' and not n.suppressed)} pages",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sloalerts", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="write synthetic metrics.csv and labels.json")
    gen.add_argument("--out", default="data")
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument("--weeks", type=int, default=4)
    gen.set_defaults(func=_generate)

    ev = sub.add_parser("eval", help="compare detectors on labeled data")
    ev.add_argument("--metrics", help="CSV/JSON metrics file; default is generated data")
    ev.add_argument("--labels", help="labels JSON with an 'incidents' list")
    ev.add_argument("--seed", type=int, default=42)
    ev.add_argument("--weeks", type=int, default=4)
    ev.add_argument("--grace-min", type=int, default=60, help="late detections still count for this long")
    ev.add_argument("--markdown", help="also write the table to this file")
    ev.set_defaults(func=_eval)

    det = sub.add_parser("detect", help="run detectors and the alert manager on a metrics file")
    det.add_argument("--metrics", required=True)
    det.add_argument("--service", help="service name; default is the file name")
    det.add_argument("--detectors", default="seasonal_2w,burn_rate", help="comma list, or 'all'")
    det.add_argument(
        "--maintenance",
        action="append",
        default=[],
        metavar="START,END",
        help="ISO or epoch window that holds notifications; repeatable",
    )
    det.add_argument("--jsonl", help="write every notification to this JSONL file")
    det.add_argument("--summary", help="write a markdown incident summary to this file")
    det.add_argument("--quiet", action="store_true", help="do not print notifications")
    det.set_defaults(func=_detect)

    args = parser.parse_args(argv)
    return args.func(args)
