"""
Appointment Validators

예약 생성 검증 로직
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages, TimeConstants
from app.core.constants.day_of_week import DayOfWeek
from app.core.exceptions import MediSolveAiException
from app.dtos.appointment import AppointmentWithTreatmentData
from app.models.appointment import Appointment
from app.models.hospital_slot import HospitalSlot


async def validate_appointment_time_interval(appointment_datetime: datetime) -> None:
    """예약 시간이 15분 간격인지 검증"""
    if appointment_datetime.minute % TimeConstants.SLOT_INTERVAL_MINUTES != 0:
        raise MediSolveAiException(ErrorMessages.APPOINTMENT_TIME_INVALID)


async def validate_no_duplicate_appointment(
    session: AsyncSession,
    doctor_id: int,
    appointment_datetime: datetime,
    appointment_end_datetime: datetime,
) -> None:
    """중복 예약 방지 검증 (동일 의사에게 동일 시간대 중복 불가)"""
    # 의사의 취소되지 않은 예약과 진료 항목 조회
    appointments_with_treatment = await Appointment.get_active_by_doctor_with_treatment(
        session=session, doctor_id=doctor_id
    )

    # 시간 겹침: 새 예약 시작 < 기존 예약 종료 AND 새 예약 종료 > 기존 예약 시작
    for data in appointments_with_treatment:
        existing_end = data.appointment_datetime + timedelta(minutes=data.treatment_duration_minutes)
        if appointment_datetime < existing_end and appointment_end_datetime > data.appointment_datetime:
            raise MediSolveAiException(ErrorMessages.APPOINTMENT_ALREADY_EXISTS)


async def check_slot_capacity_available(
    session: AsyncSession,
    slot_datetime: datetime,
    appointment_date: date,
    all_appointments: list["AppointmentWithTreatmentData"],
    treatment_duration_minutes: int,
    day_of_week_enum: DayOfWeek | None = None,
) -> bool:
    """
    특정 시간대 슬롯의 수용 인원 확인 (공통 함수)
    예약이 걸치는 모든 30분 슬롯을 확인하여 수용 인원이 충분한지 반환

    Returns:
        True: 예약 가능 (수용 인원 여유 있음)
        False: 예약 불가 (수용 인원 초과)
    """
    # 예약이 걸치는 모든 30분 슬롯 계산
    # 예: 10:15 시작 → 10:00~10:30, 10:30~11:00 슬롯 확인 필요
    slot_start = slot_datetime.replace(minute=(slot_datetime.minute // 30) * 30, second=0, microsecond=0)

    # 진료 항목의 소요 시간 사용
    slot_end_datetime = slot_datetime + timedelta(minutes=treatment_duration_minutes)

    slots_to_check = []
    current_slot_start = slot_start
    while current_slot_start < slot_end_datetime:
        current_slot_end = current_slot_start + timedelta(minutes=TimeConstants.TREATMENT_UNIT_MINUTES)
        slots_to_check.append((current_slot_start, current_slot_end))
        current_slot_start = current_slot_end

    # 각 슬롯별로 수용 인원 확인
    for slot_start_time, slot_end_time in slots_to_check:
        slot_time = slot_start_time.time()

        # HospitalSlot에서 최대 수용 인원 조회
        max_capacity = await HospitalSlot.get_default_capacity(
            session=session,
            slot_time=slot_time,
            day_of_week=day_of_week_enum,
        )

        # 해당 슬롯과 겹치는 예약 수 계산
        # 주의: all_appointments는 이미 해당 날짜로 필터링된 데이터여야 함
        count = 0
        for appointment_data in all_appointments:
            appointment_end = appointment_data.appointment_datetime + timedelta(
                minutes=appointment_data.treatment_duration_minutes
            )

            # 시간 겹침 확인
            if appointment_data.appointment_datetime < slot_end_time and slot_start_time < appointment_end:
                count += 1

        # 수용 인원 초과 시 False 반환
        if count >= max_capacity:
            return False

    return True


async def check_doctor_available(
    doctor_appointments: list[AppointmentWithTreatmentData],
    slot_datetime: datetime,
    slot_end_datetime: datetime,
    appointment_date: date,
) -> bool:
    """
    의사가 특정 시간대에 예약 가능한지 확인 (공통 함수)
    주의: doctor_appointments는 이미 해당 날짜로 필터링된 데이터여야 함

    Returns:
        True: 예약 가능 (의사 스케줄 비어있음)
        False: 예약 불가 (의사 스케줄 겹침)
    """
    for appointment_data in doctor_appointments:
        appointment_end = appointment_data.appointment_datetime + timedelta(
            minutes=appointment_data.treatment_duration_minutes
        )

        # 시간 겹침 확인
        if slot_datetime < appointment_end and slot_end_datetime > appointment_data.appointment_datetime:
            return False

    return True


async def validate_slot_capacity(
    session: AsyncSession,
    appointment_datetime: datetime,
    appointment_end_datetime: datetime,
    day_of_week: int | None = None,
) -> None:
    """
    병원 시간대별 최대 인원수 제한 검증
    예시:
        예약: 10:15~10:45 (30분)
        걸치는 슬롯: 10:00~10:30, 10:30~11:00
        각 슬롯별로 기존 예약 수를 확인하고, 최대 수용 인원을 초과하면 에러 발생
    """
    # 예약이 걸치는 모든 30분 슬롯 계산
    slot_start = appointment_datetime.replace(minute=(appointment_datetime.minute // 30) * 30, second=0, microsecond=0)

    slots_to_check = []
    current_slot_start = slot_start
    while current_slot_start < appointment_end_datetime:
        current_slot_end = current_slot_start + timedelta(minutes=TimeConstants.TREATMENT_UNIT_MINUTES)
        slots_to_check.append((current_slot_start, current_slot_end))
        current_slot_start = current_slot_end

    # 모든 취소되지 않은 예약 조회
    all_appointments = await Appointment.get_active_with_treatment(session=session)

    # 요일 변환
    day_of_week_enum = None
    if day_of_week is not None:
        day_of_week_enum = DayOfWeek(day_of_week)

    # 각 슬롯별로 수용 인원 확인
    for slot_start_time, slot_end_time in slots_to_check:
        slot_time = slot_start_time.time()

        max_capacity = await HospitalSlot.get_default_capacity(
            session=session,
            slot_time=slot_time,
            day_of_week=day_of_week_enum,
        )

        # 겹치는 예약 수 계산
        count = 0
        for data in all_appointments:
            appointment_end = data.appointment_datetime + timedelta(minutes=data.treatment_duration_minutes)

            is_overlapping = data.appointment_datetime < slot_end_time and slot_start_time < appointment_end

            if is_overlapping:
                count += 1

        # 수용 인원 초과 시 에러 발생
        if count >= max_capacity:
            raise MediSolveAiException(ErrorMessages.APPOINTMENT_CAPACITY_FULL)
