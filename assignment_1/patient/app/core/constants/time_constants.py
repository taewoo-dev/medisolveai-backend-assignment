"""시간 관련 상수"""

from __future__ import annotations

from enum import Enum


class TimeConstants(int, Enum):
    """시간 관련 상수"""

    SLOT_INTERVAL_MINUTES = 15  # 예약 시간 간격 (분)
    TREATMENT_UNIT_MINUTES = 30  # 진료 시간 단위 (분)
    DEFAULT_CAPACITY = 3  # 시간대별 기본 수용 인원

    # 예약 제한
    MAX_ADVANCE_BOOKING_DAYS = 30  # 최대 예약 가능 일수
    MIN_ADVANCE_BOOKING_HOURS = 2  # 최소 예약 시간 (시간)
