"""Default SLOs, detector suite, and alert policy used by the CLI and the evaluation."""

from __future__ import annotations

from .alerts import AlertPolicy
from .burnrate import SLO, BurnRateDetector
from .detectors import EWMA, AnyOf, Detector, RollingZScore, SeasonalBaseline, StaticThreshold, Threshold, Watch
from .model import Severity

AVAILABILITY_SLO = SLO("availability", 0.999)
LATENCY_SLO = SLO("latency", 0.99, latency_threshold_ms=400)

WATCHES = (
    Watch("requests", "both", min_delta=50),
    Watch("error_rate", "up", min_delta=0.005),
    Watch("p99_ms", "up", min_delta=100),
)


def default_detectors() -> list[Detector]:
    seasonal_2w = SeasonalBaseline(WATCHES, weeks=2)
    burn = BurnRateDetector((AVAILABILITY_SLO, LATENCY_SLO))
    return [
        StaticThreshold(
            [
                Threshold("error_rate", ">", 0.05, Severity.PAGE),
                Threshold("p99_ms", ">", 1500, Severity.PAGE),
                Threshold("requests", "<", 100, Severity.PAGE),
            ]
        ),
        RollingZScore(WATCHES, window=60, threshold=4.0),
        EWMA(WATCHES, alpha=0.05, threshold=4.0),
        SeasonalBaseline(WATCHES, weeks=1),
        seasonal_2w,
        burn,
        AnyOf([seasonal_2w, burn], name="seasonal_2w+burn_rate"),
    ]


def detector_by_name(names: list[str]) -> list[Detector]:
    known = {d.name: d for d in default_detectors()}
    if names == ["all"]:
        return list(known.values())
    missing = [n for n in names if n not in known]
    if missing:
        raise SystemExit(f"unknown detector(s): {', '.join(missing)}; choose from {', '.join(known)}")
    return [known[n] for n in names]


DEFAULT_POLICY = AlertPolicy(pending_s=120, resolve_s=900)
