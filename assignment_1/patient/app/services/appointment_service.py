"""
Appointment Service

예약 생성 및 조회 서비스
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages, HospitalOperationConstants, TimeConstants, VisitType
from app.core.constants.day_of_week import DayOfWeek
from app.core.database.connection_async import get_async_session
from app.core.exceptions import MediSolveAiException
from app.dtos.appointment import (
    AppointmentResponse,
    AppointmentWithTreatmentData,
    AvailableTimeResponse,
    CreateAppointmentRequest,
)
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.treatment import Treatment
from app.services.appointment_validators import (
    check_doctor_available,
    check_slot_capacity_available,
    validate_appointment_time_interval,
    validate_no_duplicate_appointment,
    validate_slot_capacity,
)

# ============================================================================
# 메인 서비스 함수
# ============================================================================


async def service_create_appointment(request: CreateAppointmentRequest) -> AppointmentResponse:
    """예약 생성"""
    async with get_async_session() as session:
        # 1. 환자 조회 또는 생성
        patient = await Patient.get_or_create(
            session=session,
            name=request.patient_name,
            phone=request.patient_phone,
        )

        # 2. 의사 존재 및 활성 상태 확인
        doctor = await _validate_doctor(session=session, doctor_id=request.doctor_id)

        # 3. 진료 항목 존재 및 활성 상태 확인
        treatment = await _validate_treatment(session=session, treatment_id=request.treatment_id)

        # 4. 예약 시간 검증
        appointment_datetime = request.appointment_datetime
        appointment_end_datetime = appointment_datetime + timedelta(minutes=treatment.duration_minutes)

        # 4-1. 예약 시간이 15분 간격인지 확인
        await validate_appointment_time_interval(appointment_datetime)

        # 4-2. 중복 예약 방지 (동일 의사에게 동일 시간대 중복 불가)
        await validate_no_duplicate_appointment(
            session=session,
            doctor_id=request.doctor_id,
            appointment_datetime=appointment_datetime,
            appointment_end_datetime=appointment_end_datetime,
        )

        # 4-3. 병원 시간대별 최대 인원수 제한 검증 (HospitalSlot 사용)
        day_of_week_enum = _get_day_of_week_enum(appointment_datetime)

        await validate_slot_capacity(
            session=session,
            appointment_datetime=appointment_datetime,
            appointment_end_datetime=appointment_end_datetime,
            day_of_week=day_of_week_enum.value,
        )

        # 5. 초진/재진 자동 판단
        has_completed = await patient.has_completed_appointment(session=session)
        visit_type = VisitType.determine_visit_type(has_previous_completed_visit=has_completed)

        # 6. 예약 생성
        appointment = await Appointment.create_one(
            session=session,
            patient_id=patient.id,
            doctor_id=doctor.id,
            treatment_id=treatment.id,
            appointment_datetime=appointment_datetime,
            visit_type=visit_type,
            memo=request.memo,
        )

        await session.commit()
        await session.refresh(appointment)
        await session.refresh(appointment.doctor)
        await session.refresh(appointment.treatment)

        return AppointmentResponse(
            id=appointment.id,
            patient_name=patient.name,
            patient_phone=patient.phone,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            treatment_id=treatment.id,
            treatment_name=treatment.name,
            appointment_datetime=appointment.appointment_datetime,
            status=appointment.status.value,
            visit_type=appointment.visit_type.value,
            memo=appointment.memo,
        )


async def service_get_available_times(
    doctor_id: int, treatment_id: int, appointment_date: date
) -> AvailableTimeResponse:
    """예약 가능 시간 조회"""
    async with get_async_session() as session:
        # 1. 의사 존재 및 활성 상태 확인
        await _validate_doctor(session=session, doctor_id=doctor_id)

        # 2. 진료 항목 존재 및 활성 상태 확인
        treatment = await _validate_treatment(session=session, treatment_id=treatment_id)

        # 3. 날짜가 운영일인지 확인
        day_of_week_enum = _check_is_operation_day(appointment_date)
        if day_of_week_enum is None:
            # 휴무일이면 빈 리스트 반환
            return AvailableTimeResponse(
                doctor_id=doctor_id,
                date=appointment_date.isoformat(),
                available_times=[],
            )

        # 4. 해당 날짜의 15분 간격 시간대 생성 (운영 시간 내, 진료 항목 소요 시간 고려)
        time_slots = _generate_time_slots(appointment_date, treatment.duration_minutes)

        # 5. 해당 의사의 기존 예약 조회 (해당 날짜만)
        doctor_appointments = await Appointment.get_active_by_doctor_with_treatment(
            session=session, doctor_id=doctor_id, appointment_date=appointment_date
        )

        # 6. 해당 날짜의 모든 예약 조회 (수용 인원 확인용)
        all_appointments = await Appointment.get_active_with_treatment(
            session=session, appointment_date=appointment_date
        )

        # 7. 각 시간대별로 예약 가능 여부 확인
        available_times = []
        for slot_datetime in time_slots:
            is_available = await _is_time_slot_available(
                session=session,
                slot_datetime=slot_datetime,
                appointment_date=appointment_date,
                doctor_appointments=doctor_appointments,
                all_appointments=all_appointments,
                day_of_week_enum=day_of_week_enum,
                treatment_duration_minutes=treatment.duration_minutes,
            )

            if is_available:
                slot_time = slot_datetime.time()
                available_times.append(slot_time.strftime("%H:%M"))

        return AvailableTimeResponse(
            doctor_id=doctor_id,
            date=appointment_date.isoformat(),
            available_times=available_times,
        )


async def service_get_appointments(patient_phone: str) -> list[AppointmentResponse]:
    """환자 예약 목록 조회"""
    async with get_async_session() as session:
        # 환자 전화번호로 예약 목록 조회 (최신순)
        appointments = await Appointment.get_by_patient_phone(session=session, patient_phone=patient_phone)

        # AppointmentResponse 리스트로 변환
        return [
            AppointmentResponse(
                id=appointment.id,
                patient_name=appointment.patient.name,
                patient_phone=appointment.patient.phone,
                doctor_id=appointment.doctor.id,
                doctor_name=appointment.doctor.name,
                treatment_id=appointment.treatment.id,
                treatment_name=appointment.treatment.name,
                appointment_datetime=appointment.appointment_datetime,
                status=appointment.status.value,
                visit_type=appointment.visit_type.value,
                memo=appointment.memo,
            )
            for appointment in appointments
        ]


async def service_cancel_appointment(appointment_id: int, patient_phone: str) -> AppointmentResponse:
    """예약 취소"""

    from app.core.constants.error_messages import ErrorMessages
    from app.core.exceptions import MediSolveAiException

    async with get_async_session() as session:
        # 1. 예약 조회 및 본인 확인
        appointment = await Appointment.get_by_id_and_patient_phone(
            session=session, appointment_id=appointment_id, patient_phone=patient_phone
        )

        if appointment is None:
            raise MediSolveAiException(ErrorMessages.APPOINTMENT_NOT_FOUND)

        # 2. 예약 취소
        await appointment.cancel(session=session)

        await session.commit()
        await session.refresh(appointment)
        await session.refresh(appointment, attribute_names=["doctor", "patient", "treatment"])

        return AppointmentResponse(
            id=appointment.id,
            patient_name=appointment.patient.name,
            patient_phone=appointment.patient.phone,
            doctor_id=appointment.doctor.id,
            doctor_name=appointment.doctor.name,
            treatment_id=appointment.treatment.id,
            treatment_name=appointment.treatment.name,
            appointment_datetime=appointment.appointment_datetime,
            status=appointment.status.value,
            visit_type=appointment.visit_type.value,
            memo=appointment.memo,
        )


# ============================================================================
# 헬퍼 함수
# ============================================================================


async def _validate_doctor(session: AsyncSession, doctor_id: int) -> Doctor:
    """의사 존재 및 활성 상태 검증"""
    doctor = await Doctor.get_by_id(session=session, doctor_id=doctor_id)
    if doctor is None or not doctor.is_active:
        raise MediSolveAiException(ErrorMessages.DOCTOR_NOT_FOUND)
    return doctor


async def _validate_treatment(session: AsyncSession, treatment_id: int) -> Treatment:
    """진료 항목 존재 및 활성 상태 검증"""
    treatment = await Treatment.get_by_id(session=session, treatment_id=treatment_id)
    if treatment is None or not treatment.is_active:
        raise MediSolveAiException(ErrorMessages.TREATMENT_NOT_FOUND)
    return treatment


def _get_day_of_week_enum(datetime_or_date: datetime | date) -> DayOfWeek:
    """datetime 또는 date에서 요일 enum 반환"""
    day_of_week = datetime_or_date.weekday()  # 0=월요일, 6=일요일
    return DayOfWeek.from_python_weekday(day_of_week)


def _check_is_operation_day(appointment_date: date) -> DayOfWeek | None:
    """운영일 여부 확인 및 요일 enum 반환"""
    day_of_week_enum = _get_day_of_week_enum(appointment_date)
    if HospitalOperationConstants.is_closed_day(day_of_week_enum):
        return None
    return day_of_week_enum


def _generate_time_slots(appointment_date: date, treatment_duration_minutes: int) -> list[datetime]:
    """해당 날짜의 15분 간격 시간대 생성 (운영 시간 내, 점심시간 및 퇴근시간과 겹치지 않음)"""
    open_time = time.fromisoformat(HospitalOperationConstants.DEFAULT_OPEN_TIME)
    close_time = time.fromisoformat(HospitalOperationConstants.DEFAULT_CLOSE_TIME)
    lunch_start = time.fromisoformat(HospitalOperationConstants.DEFAULT_LUNCH_START)
    lunch_end = time.fromisoformat(HospitalOperationConstants.DEFAULT_LUNCH_END)

    # 날짜와 시간을 결합하여 datetime 생성
    start_datetime = datetime.combine(appointment_date, open_time)
    end_datetime = datetime.combine(appointment_date, close_time)

    # 15분 간격으로 시간대 생성
    time_slots = []
    current_time = start_datetime
    while current_time < end_datetime:
        current_time_obj = current_time.time()

        # 예약 종료 시간 계산 (진료 항목의 소요 시간 사용)
        appointment_end_time = current_time + timedelta(minutes=treatment_duration_minutes)
        appointment_end_time_obj = appointment_end_time.time()

        # 예약이 점심시간과 겹치는지 확인
        # 겹침 조건: 예약 시작 < 점심 종료 AND 예약 종료 > 점심 시작
        # 예: 11:45 시작 → 12:15 종료 (점심시간 12:00~13:00과 겹침)
        if current_time_obj < lunch_end and appointment_end_time_obj > lunch_start:
            current_time += timedelta(minutes=TimeConstants.SLOT_INTERVAL_MINUTES)
            continue

        # 예약 종료 시간이 퇴근시간을 넘어가는지 확인
        # 예: 17:45 시작 → 18:15 종료 (퇴근시간 18:00을 넘어감)
        if appointment_end_time_obj > close_time:
            current_time += timedelta(minutes=TimeConstants.SLOT_INTERVAL_MINUTES)
            continue

        time_slots.append(current_time)
        current_time += timedelta(minutes=TimeConstants.SLOT_INTERVAL_MINUTES)

    return time_slots


async def _is_time_slot_available(
    session: AsyncSession,
    slot_datetime: datetime,
    appointment_date: date,
    doctor_appointments: list[AppointmentWithTreatmentData],
    all_appointments: list[AppointmentWithTreatmentData],
    day_of_week_enum: DayOfWeek,
    treatment_duration_minutes: int,
) -> bool:
    """특정 시간대가 예약 가능한지 확인"""
    # 의사 예약 여부 확인 (진료 항목의 소요 시간 사용)
    slot_end_datetime = slot_datetime + timedelta(minutes=treatment_duration_minutes)
    is_doctor_available = await check_doctor_available(
        doctor_appointments=doctor_appointments,
        slot_datetime=slot_datetime,
        slot_end_datetime=slot_end_datetime,
        appointment_date=appointment_date,
    )

    if not is_doctor_available:
        return False

    # 병원 수용 인원 확인
    is_capacity_available = await check_slot_capacity_available(
        session=session,
        slot_datetime=slot_datetime,
        appointment_date=appointment_date,
        all_appointments=all_appointments,
        treatment_duration_minutes=treatment_duration_minutes,
        day_of_week_enum=day_of_week_enum,
    )

    return is_capacity_available
