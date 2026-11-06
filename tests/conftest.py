from collections.abc import Callable, Sequence

import pytest

from sloalerts.series import Series

T0 = 1_767_571_200  # Monday 00:00 UTC


def make_series(
    n: int,
    step: int = 60,
    requests: float | Sequence[float] = 1000.0,
    errors: float | Sequence[float] = 0.0,
    p50: float | Sequence[float] = 50.0,
    p90: float | Sequence[float] = 100.0,
    p99: float | Sequence[float] = 200.0,
) -> Series:
    def col(v: float | Sequence[float]) -> list[float]:
        return [float(x) for x in v] if isinstance(v, Sequence) else [float(v)] * n

    return Series([T0 + i * step for i in range(n)], col(requests), col(errors), col(p50), col(p90), col(p99))


@pytest.fixture
def series_factory() -> Callable[..., Series]:
    return make_series
