from sloalerts.alerts import AlertManager, AlertPolicy, MaintenanceWindow
from sloalerts.model import Severity, Signal

STEP = 60
TS = [i * STEP for i in range(30)]


def sig(i: int, detector: str = "d", metric: str = "m", sev: Severity = Severity.TICKET) -> Signal:
    return Signal(TS[i], detector, metric, sev, 10.0, 1.0, f"{detector}/{metric} is high")


def run(signals: list[Signal], **policy: object) -> AlertManager:
    manager = AlertManager(AlertPolicy(**policy))
    manager.run(TS, signals)
    return manager


def events(manager: AlertManager) -> list[tuple[int, str]]:
    return [(n.ts // STEP, n.event) for n in manager.notifications]


def test_pending_period_delays_the_open():
    m = run([sig(i) for i in range(5)], pending_s=120)
    assert len(m.alerts) == 1
    assert m.alerts[0].first_seen == TS[0]
    assert m.alerts[0].opened_at == TS[2]


def test_short_blip_never_opens():
    m = run([sig(0), sig(1)], pending_s=120)
    assert m.alerts == []
    assert m.notifications == []


def test_broken_streak_restarts_the_pending_clock():
    m = run([sig(0), sig(1), sig(3), sig(4)], pending_s=120)
    assert m.alerts == []


def test_resolve_waits_for_quiet_time():
    m = run([sig(i) for i in range(5)], pending_s=0, resolve_s=300)
    assert m.alerts[0].resolved_at == TS[9]
    assert events(m) == [(0, "open"), (9, "resolve")]


def test_short_gap_keeps_one_alert():
    m = run([sig(i) for i in (0, 1, 2, 3, 4, 7, 8)], pending_s=0, resolve_s=300)
    assert len(m.alerts) == 1


def test_duplicate_and_repeated_signals_are_deduplicated():
    signals = [sig(i) for i in range(10)] + [sig(i) for i in range(10)]
    m = run(signals, pending_s=0)
    assert len(m.alerts) == 1
    assert [e for _, e in events(m)] == ["open", "resolve"]


def test_related_alerts_group_into_one_page():
    signals = [sig(i, "seasonal", "requests", Severity.PAGE) for i in range(5)]
    signals += [sig(i, "zscore", "requests", Severity.PAGE) for i in range(2, 7)]
    m = run(signals, pending_s=0)
    assert len(m.alerts) == 2
    assert len(m.groups) == 1
    assert [(n.event, n.route) for n in m.notifications if n.ts < TS[10]] == [("open", "pager"), ("update", "log")]


def test_group_by_metric_splits_groups():
    signals = [sig(i, metric="a") for i in range(3)] + [sig(i, metric="b") for i in range(3)]
    m = run(signals, pending_s=0, group_by=("metric",))
    assert len(m.groups) == 2


def test_severity_escalation_sends_a_second_notification():
    signals = [sig(i) for i in range(3)] + [sig(i, sev=Severity.PAGE) for i in range(3, 6)]
    m = run(signals, pending_s=0)
    assert [(n.event, n.route) for n in m.notifications][:2] == [("open", "ticket"), ("escalate", "pager")]


def test_flapping_alert_is_held_back():
    m = run([sig(i) for i in range(0, 12, 2)], pending_s=0, resolve_s=60, flap_max_opens=3)
    assert len(m.alerts) == 6
    assert [a.flapping for a in m.alerts] == [False, False, True, True, True, True]
    assert [e for _, e in events(m)] == ["open", "resolve", "open", "resolve", "flapping"]


def test_custom_routes():
    m = run(
        [sig(i, sev=Severity.PAGE) for i in range(3)],
        pending_s=0,
        routes={Severity.PAGE: "oncall", Severity.TICKET: "queue"},
    )
    assert m.notifications[0].route == "oncall"


def test_maintenance_holds_then_delivers_after_the_window():
    window = MaintenanceWindow(TS[0], TS[5])
    m = AlertManager(AlertPolicy(pending_s=0), [window])
    m.run(TS, [sig(i) for i in range(10)])
    opens = [(n.ts // STEP, n.suppressed) for n in m.notifications if n.event == "open"]
    assert opens == [(0, "maintenance"), (5, None)]


def test_alert_inside_maintenance_never_pages_or_resolves():
    m = AlertManager(AlertPolicy(pending_s=0, resolve_s=60), [MaintenanceWindow(TS[0], TS[20])])
    m.run(TS, [sig(i) for i in range(3)])
    assert [(n.event, n.suppressed) for n in m.notifications] == [("open", "maintenance")]
    assert m.groups[0].notified is None


def test_maintenance_for_another_service_does_not_apply():
    m = AlertManager(AlertPolicy(pending_s=0), [MaintenanceWindow(TS[0], TS[20], service="other")])
    m.run(TS, [sig(i) for i in range(3)])
    assert m.notifications[0].suppressed is None
