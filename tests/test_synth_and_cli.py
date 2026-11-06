import json
from itertools import pairwise
from statistics import mean

from sloalerts.cli import main
from sloalerts.synth import INCIDENT_KINDS, generate


def test_generation_is_deterministic():
    a, b = generate(seed=3, weeks=2, per_kind=1), generate(seed=3, weeks=2, per_kind=1)
    assert a.series.requests == b.series.requests
    assert a.incidents == b.incidents
    assert generate(seed=4, weeks=2, per_kind=1).series.requests != a.series.requests


def test_incidents_cover_every_kind_after_warmup_without_overlap():
    data = generate(seed=1, weeks=3, per_kind=2)
    assert sorted({i.kind for i in data.incidents}) == sorted(INCIDENT_KINDS)
    assert all(i.start >= data.series.ts[0] + 7 * 86400 for i in data.incidents)
    spans = sorted((i.start, i.end) for i in data.incidents + data.noise)
    assert all(a_end <= b_start for (_, a_end), (b_start, _) in pairwise(spans))


def test_traffic_drop_keeps_availability_near_100_percent():
    data = generate(seed=5, weeks=2, per_kind=1)
    s = data.series
    drop = next(i for i in data.incidents if i.kind == "traffic_drop")
    during = range(s.index_of(drop.start), s.index_of(drop.end))
    week_before = [i - 7 * 1440 for i in during]
    ratio = mean(s.requests[i] for i in during) / mean(s.requests[i] for i in week_before)
    assert 0.5 < ratio < 0.6
    availability = 1 - sum(s.errors[i] for i in during) / sum(s.requests[i] for i in during)
    assert availability > 0.999


def test_cli_eval_prints_the_table(capsys):
    assert main(["eval", "--weeks", "2"]) == 0
    out = capsys.readouterr().out
    assert "| Incident type | static | zscore | ewma |" in out
    assert "**Precision**" in out


def test_cli_generate_then_detect(tmp_path, capsys):
    main(["generate", "--out", str(tmp_path), "--weeks", "2", "--seed", "9"])
    labels = json.loads((tmp_path / "labels.json").read_text())
    assert labels["incidents"] and labels["noise"]
    main(
        [
            "detect",
            "--metrics",
            str(tmp_path / "metrics.csv"),
            "--jsonl",
            str(tmp_path / "n.jsonl"),
            "--summary",
            str(tmp_path / "s.md"),
            "--maintenance",
            "2026-01-05T00:00:00Z,2026-01-06T00:00:00Z",
        ]
    )
    lines = (tmp_path / "n.jsonl").read_text().splitlines()
    assert lines and all(json.loads(line)["event"] for line in lines)
    assert (tmp_path / "s.md").read_text().startswith("# Incident summary: metrics")
    main(["eval", "--metrics", str(tmp_path / "metrics.csv"), "--labels", str(tmp_path / "labels.json")])
    assert "seasonal_2w+burn_rate" in capsys.readouterr().out
