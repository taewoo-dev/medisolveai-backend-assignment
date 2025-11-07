"""에러 메시지 상수"""

from __future__ import annotations


class ErrorMessages:
    """에러 메시지 상수"""

    # 예약 관련
    APPOINTMENT_NOT_FOUND = "예약을 찾을 수 없습니다."
    APPOINTMENT_ALREADY_EXISTS = "해당 시간에 이미 예약이 있습니다."
    APPOINTMENT_CAPACITY_FULL = "해당 시간대의 예약이 가득 찼습니다."
    APPOINTMENT_TIME_INVALID = "유효하지 않은 예약 시간입니다."
    APPOINTMENT_TOO_EARLY = "예약은 최소 2시간 전에 해야 합니다."
    APPOINTMENT_TOO_LATE = "예약은 최대 30일 전까지만 가능합니다."
    APPOINTMENT_ALREADY_CANCELLED = "이미 취소된 예약입니다."
    APPOINTMENT_NOT_OWNED = "본인의 예약만 취소할 수 있습니다."

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
