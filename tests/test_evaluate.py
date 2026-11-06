import pytest

from sloalerts.alerts import Alert, AlertPolicy
from sloalerts.detectors import StaticThreshold, Threshold
from sloalerts.evaluate import comparison_table, evaluate, fmt_duration, matches, score
from sloalerts.model import Incident, Severity

HOUR = 3600


def alert(opened_at: int) -> Alert:
    return Alert("A", "svc", "d", "m", Severity.TICKET, opened_at, opened_at, opened_at, 1.0, 0.0, "")


INCIDENTS = [
    Incident("I1", "traffic_drop", 10 * HOUR, 11 * HOUR),
    Incident("I2", "traffic_drop", 50 * HOUR, 51 * HOUR),
    Incident("I3", "error_spike", 90 * HOUR, 90 * HOUR + 900),
]


def test_match_window_includes_grace():
    inc = INCIDENTS[0]
    assert matches(alert(inc.start), inc, 0)
    assert not matches(alert(inc.start - 1), inc, HOUR)
    assert matches(alert(inc.end + HOUR), inc, HOUR)
    assert not matches(alert(inc.end + HOUR + 1), inc, HOUR)


def test_precision_recall_and_time_to_detect():
    alerts = [alert(10 * HOUR + 300), alert(10 * HOUR + 600), alert(30 * HOUR), alert(90 * HOUR + 120)]
    s = score("x", alerts, INCIDENTS, weeks=1.0, grace_s=HOUR)
    assert s.true_alerts == 3
    assert s.false_alerts == 1
    assert s.precision == pytest.approx(0.75)
    assert s.recall == pytest.approx(2 / 3)
    assert s.per_kind["traffic_drop"].detected == 1
    assert s.per_kind["traffic_drop"].ttd_s == [300]  # earliest alert counts
    assert s.per_kind["error_spike"].median_ttd_s == 120


def test_no_alerts_means_no_precision():
    s = score("quiet", [], INCIDENTS, weeks=1.0)
    assert s.precision is None
    assert s.recall == 0.0


def test_comparison_table_layout():
    a = score("a", [alert(10 * HOUR + 120)], INCIDENTS, weeks=2.0)
    b = score("b", [], INCIDENTS, weeks=2.0)
    table = comparison_table([a, b])
    assert "| Incident type | a | b |" in table
    assert "| traffic_drop (n=2) | 1/2 in 2m | 0/2 |" in table
    assert "| **Precision** | 100% | n/a |" in table
    assert table.index("traffic_drop") < table.index("error_spike")


def test_fmt_duration():
    assert fmt_duration(240) == "4m"
    assert fmt_duration(3 * HOUR) == "3.0h"


def test_evaluate_end_to_end(series_factory):
    errors = [0.0] * 30 + [100.0] * 10 + [0.0] * 20
    s = series_factory(60, requests=1000, errors=errors)
    inc = [Incident("I1", "error_spike", s.ts[30], s.ts[40])]
    det = StaticThreshold([Threshold("error_rate", ">", 0.05)])
    [result] = evaluate(s, inc, [det], AlertPolicy(pending_s=120))
    assert result.recall == 1.0
    assert result.per_kind["error_spike"].ttd_s == [120]
    assert result.precision == 1.0
