"""退避计算单元测试。"""

import math

from backend.infrastructure.async_task.relay.service import compute_backoff_delay

BASE = 1.0
MAX_DELAY = 60.0
NO_JITTER = lambda low, high: 0.0  # noqa: E731


def test_first_attempt_uses_base_delay():
    assert compute_backoff_delay(1, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY, jitter=NO_JITTER) == BASE


def test_exponential_growth():
    for attempts, expected in [(1, 1.0), (2, 2.0), (3, 4.0), (4, 8.0)]:
        assert compute_backoff_delay(
            attempts, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY, jitter=NO_JITTER
        ) == expected


def test_capped_at_max_delay():
    assert compute_backoff_delay(
        20, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY, jitter=NO_JITTER
    ) == MAX_DELAY


def test_jitter_keeps_value_in_range():
    for attempts in range(1, 10):
        value = compute_backoff_delay(
            attempts, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY
        )
        raw = min(BASE * 2 ** (attempts - 1), MAX_DELAY)
        assert raw <= value <= raw + min(0.5, raw) + 1e-9


def test_zero_attempts_treated_as_first():
    assert compute_backoff_delay(
        0, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY, jitter=NO_JITTER
    ) == BASE


def test_is_finite():
    assert math.isfinite(compute_backoff_delay(5, base_delay_seconds=BASE, max_delay_seconds=MAX_DELAY))
