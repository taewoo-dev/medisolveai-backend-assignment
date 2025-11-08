"""Assignment 2 난수 생성 유틸리티 테스트."""

from __future__ import annotations

import math

import pytest

from random_generator import get_random, get_1_or_0


def test_get_random_returns_within_bounds():
    """`get_random`이 항상 범위 내 값을 반환하는지 확인한다."""
    for n in range(1, 32):
        value = get_random(n)
        assert 0 <= value <= n

def test_get_random_zero():
    """n=0 입력일 때 항상 0을 반환하는지 확인한다."""
    assert get_random(0) == 0


def test_get_random_negative_raises():
    """음수 입력 시 ValueError가 발생하는지 검증한다."""
    with pytest.raises(ValueError):
        get_random(-1)


def test_get_random_basic_values():
    """간단한 정수 입력에 대해 기본적인 범위 검증을 수행한다."""
    for value in [0, 1, 2, 5]:
        assert 0 <= get_random(value) <= value


def test_get_random_float_flooring():
    """실수 입력은 내림(floor)되어 처리되는지 확인한다."""
    for value, expected in [(5.0, 5), (5.3, 5), (5.999, 5)]:
        result = get_random(value)
        assert isinstance(result, int)
        assert 0 <= result <= expected


def test_get_random_invalid_float_inputs():
    """무한대 혹은 NaN 입력이 ValueError를 발생시키는지 확인한다."""
    with pytest.raises(ValueError):
        get_random(float("inf"))
    with pytest.raises(ValueError):
        get_random(float("nan"))


def test_get_random_invalid_type():
    """지원하지 않는 타입 입력이 TypeError를 발생시키는지 확인한다."""
    with pytest.raises(TypeError):
        get_random("가나다")


def test_get_random_rejects_out_of_range_candidates(monkeypatch):
    """허용 범위를 벗어난 후보가 거절(rejection)되는지 확인한다."""

    sequence = iter([1, 1, 1, 0, 1, 1])  # 111 => 7 (>5) 후 011 => 3

    def fake_get_1_or_0() -> int:
        try:
            return next(sequence)
        except StopIteration:  # pragma: no cover - 안전 장치
            return 0

    module_path = f"{get_1_or_0.__module__}.get_1_or_0"
    monkeypatch.setattr(module_path, fake_get_1_or_0)

    assert get_random(5) == 3


def test_get_random_distribution_quality():
    """기대값 대비 빈도가 5σ 이내인지 통계적으로 검증한다."""

    n = 7
    sample_size = 120_000
    counts = [0 for _ in range(n + 1)]

    for _ in range(sample_size):
        counts[get_random(n)] += 1

    expected = sample_size / (n + 1)
    sigma = math.sqrt(expected * (1 - 1 / (n + 1)))
    tolerance = 5 * sigma

    for count in counts:
        assert abs(count - expected) <= tolerance


def test_get_random_large_n_rejection_behaviour_small(monkeypatch):
    """작은 bit_length 케이스에서 rejection 동작을 검증한다."""

    bit_length = 12
    offset = 129
    n = (1 << bit_length) - offset

    first_candidate_bits = [1] * bit_length
    second_candidate_bits = [0] * bit_length

    calls = {"count": 0}

    def fake_get_1_or_0() -> int:
        calls["count"] += 1
        try:
            return next(bits)
        except StopIteration:  # pragma: no cover - 안전 장치
            return 0

    bits = iter(first_candidate_bits + second_candidate_bits)
    module_path = f"{get_1_or_0.__module__}.get_1_or_0"
    monkeypatch.setattr(module_path, fake_get_1_or_0)

    assert get_random(n) == 0
    assert calls["count"] == bit_length * 2


def test_get_random_large_n_rejection_behaviour_huge(monkeypatch):
    """매우 큰 bit_length 케이스에서 rejection 동작을 검증한다."""

    bit_length = 2048
    offset = 321
    n = (1 << bit_length) - offset

    first_candidate_bits = [1] * bit_length
    second_candidate_bits = [0] * bit_length

    calls = {"count": 0}

    def fake_get_1_or_0() -> int:
        calls["count"] += 1
        try:
            return next(bits)
        except StopIteration:  # pragma: no cover - 안전 장치
            return 0

    bits = iter(first_candidate_bits + second_candidate_bits)
    module_path = f"{get_1_or_0.__module__}.get_1_or_0"
    monkeypatch.setattr(module_path, fake_get_1_or_0)

    assert get_random(n) == 0
    assert calls["count"] == bit_length * 2

