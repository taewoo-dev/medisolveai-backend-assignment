"""요일 상수"""

from __future__ import annotations

from enum import Enum


class DayOfWeek(int, Enum):
    """요일 상수 (MySQL DAYOFWEEK 함수 호환)"""

    SUNDAY = 1  # 일요일
    MONDAY = 2  # 월요일
    TUESDAY = 3  # 화요일
    WEDNESDAY = 4  # 수요일
    THURSDAY = 5  # 목요일
    FRIDAY = 6  # 금요일
    SATURDAY = 7  # 토요일

    @classmethod
    def from_python_weekday(cls, python_weekday: int) -> DayOfWeek:
        """Python weekday (0=월요일)를 MySQL DAYOFWEEK로 변환"""
        # Python: 0(월) ~ 6(일) -> MySQL: 1(일) ~ 7(토)
        mapping = {
            0: cls.MONDAY,  # 월요일
            1: cls.TUESDAY,  # 화요일
            2: cls.WEDNESDAY,  # 수요일
            3: cls.THURSDAY,  # 목요일
            4: cls.FRIDAY,  # 금요일
            5: cls.SATURDAY,  # 토요일
            6: cls.SUNDAY,  # 일요일
        }
        return mapping[python_weekday]

    def to_korean_name(self) -> str:
        """한국어 요일명 반환"""
        names = {
            self.SUNDAY: "일요일",
            self.MONDAY: "월요일",
            self.TUESDAY: "화요일",
            self.WEDNESDAY: "수요일",
            self.THURSDAY: "목요일",
            self.FRIDAY: "금요일",
            self.SATURDAY: "토요일",
        }
        return names[self]

    def to_short_korean_name(self) -> str:
        """한국어 요일 단축명 반환"""
        names = {
            self.SUNDAY: "일",
            self.MONDAY: "월",
            self.TUESDAY: "화",
            self.WEDNESDAY: "수",
            self.THURSDAY: "목",
            self.FRIDAY: "금",
            self.SATURDAY: "토",
        }
        return names[self]
