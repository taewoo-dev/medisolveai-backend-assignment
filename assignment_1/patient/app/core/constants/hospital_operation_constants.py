"""병원 운영 관련 상수"""

from __future__ import annotations

from .day_of_week import DayOfWeek


class HospitalOperationConstants:
    """병원 운영 관련 상수"""

    # 기본 운영 시간
    DEFAULT_OPEN_TIME = "09:00"
    DEFAULT_CLOSE_TIME = "18:00"
    DEFAULT_LUNCH_START = "12:00"
    DEFAULT_LUNCH_END = "13:00"

    # 운영 요일 (월~금)
    OPERATION_DAYS = [
        DayOfWeek.MONDAY,
        DayOfWeek.TUESDAY,
        DayOfWeek.WEDNESDAY,
        DayOfWeek.THURSDAY,
        DayOfWeek.FRIDAY,
    ]

    # 휴무일 (토, 일)
    CLOSED_DAYS = [
        DayOfWeek.SATURDAY,
        DayOfWeek.SUNDAY,
    ]

    @classmethod
    def is_operation_day(cls, day_of_week: DayOfWeek) -> bool:
        """운영일 여부 확인"""
        return day_of_week in cls.OPERATION_DAYS

    @classmethod
    def is_closed_day(cls, day_of_week: DayOfWeek) -> bool:
        """휴무일 여부 확인"""
        return day_of_week in cls.CLOSED_DAYS
