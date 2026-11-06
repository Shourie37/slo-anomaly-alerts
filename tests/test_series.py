import json

import pytest

from sloalerts.series import Series, load_series, parse_ts, save_csv


def test_parse_ts_accepts_epoch_and_iso():
    assert parse_ts(60) == 60
    assert parse_ts("60") == 60
    assert parse_ts("1970-01-01T00:01:00Z") == 60
    assert parse_ts("1970-01-01T00:01:00") == 60


def test_csv_round_trip(tmp_path, series_factory):
    s = series_factory(5, requests=[10, 20, 30, 40, 50], errors=[0, 1, 0, 2, 0])
    path = tmp_path / "m.csv"
    save_csv(s, path)
    loaded = load_series(path)
    assert loaded.ts == s.ts
    assert loaded.requests == s.requests
    assert loaded.service == "m"


def test_json_with_aliases_and_iso_timestamps(tmp_path):
    points = [
        {"timestamp": "2026-01-05T00:01:00Z", "requests": 100, "errors": 5, "p50": 10, "p90": 20, "p99": 30},
        {"timestamp": "2026-01-05T00:00:00Z", "requests": 200, "errors": 0, "p50": 10, "p90": 20, "p99": 30},
    ]
    path = tmp_path / "m.json"
    path.write_text(json.dumps({"service": "api", "points": points}))
    s = load_series(path)
    assert s.service == "api"
    assert s.requests == [200.0, 100.0]  # sorted by time
    assert s.metric("error_rate") == [0.0, 0.05]
    assert s.step == 60


def test_irregular_interval_is_rejected():
    with pytest.raises(ValueError, match="regular interval"):
        Series([0, 60, 180], [1, 1, 1], [0, 0, 0], [1, 1, 1], [1, 1, 1], [1, 1, 1])


def test_missing_column_is_rejected():
    with pytest.raises(ValueError, match="missing"):
        Series.from_rows([{"ts": 0, "requests": 1}])


def test_error_rate_with_zero_requests_is_zero(series_factory):
    s = series_factory(2, requests=[0, 10], errors=[0, 1])
    assert s.metric("error_rate") == [0.0, 0.1]
