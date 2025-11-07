"""에러 메시지 상수"""

from __future__ import annotations


class ErrorMessages:
    """에러 메시지 상수"""

    # 의사 관련
    DOCTOR_NOT_FOUND = "의사를 찾을 수 없습니다."
    DOCTOR_UPDATE_EMPTY = "업데이트할 필드가 최소 한 개 이상 필요합니다."

    # 진료 항목 관련
    TREATMENT_NOT_FOUND = "진료 항목을 찾을 수 없습니다."
    TREATMENT_UPDATE_EMPTY = "업데이트할 필드가 최소 한 개 이상 필요합니다."

    # 병원 슬롯 관련
    HOSPITAL_SLOT_NOT_FOUND = "병원 시간대를 찾을 수 없습니다."
    HOSPITAL_SLOT_UPDATE_EMPTY = "업데이트할 필드가 최소 한 개 이상 필요합니다."
    HOSPITAL_SLOT_TIME_CONFLICT = "이미 등록된 시간대입니다."
    HOSPITAL_SLOT_INVALID_INTERVAL = "시간대는 30분 간격이어야 합니다."

    # 공통
    INVALID_PAGINATION = "페이지 정보가 올바르지 않습니다."

    # 예약 관련
    APPOINTMENT_NOT_FOUND = "예약을 찾을 수 없습니다."
    APPOINTMENT_INVALID_STATUS_TRANSITION = "해당 예약 상태로 변경할 수 없습니다."
