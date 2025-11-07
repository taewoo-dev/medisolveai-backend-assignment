"""병원 관련 상수"""

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


class ErrorMessages:
    """에러 메시지 상수"""

    # 예약 관련
    APPOINTMENT_NOT_FOUND = "예약을 찾을 수 없습니다."
    APPOINTMENT_ALREADY_EXISTS = "해당 시간에 이미 예약이 있습니다."
    APPOINTMENT_CAPACITY_FULL = "해당 시간대의 예약이 가득 찼습니다."
    APPOINTMENT_TIME_INVALID = "유효하지 않은 예약 시간입니다."
    APPOINTMENT_TOO_EARLY = "예약은 최소 2시간 전에 해야 합니다."
    APPOINTMENT_TOO_LATE = "예약은 최대 30일 전까지만 가능합니다."

    # 환자 관련
    PATIENT_NOT_FOUND = "환자를 찾을 수 없습니다."
    PATIENT_PHONE_DUPLICATE = "이미 등록된 연락처입니다."

    # 의사 관련
    DOCTOR_NOT_FOUND = "의사를 찾을 수 없습니다."
    DOCTOR_NOT_AVAILABLE = "해당 의사는 현재 진료가 불가능합니다."

    # 치료 관련
    TREATMENT_NOT_FOUND = "치료 항목을 찾을 수 없습니다."
    TREATMENT_NOT_AVAILABLE = "해당 치료는 현재 이용할 수 없습니다."

    # 시스템 관련
    DATABASE_CONNECTION_ERROR = "데이터베이스 연결에 실패했습니다."
    INTERNAL_SERVER_ERROR = "내부 서버 오류가 발생했습니다."
