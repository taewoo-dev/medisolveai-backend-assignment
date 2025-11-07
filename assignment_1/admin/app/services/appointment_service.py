"""Appointment Service"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.constants.appointment_status import AppointmentStatus
from app.core.database.connection_async import get_async_session
from app.core.exceptions import MediSolveAiException
from app.dtos.appointment import (
    AppointmentDailyCountItem,
    AppointmentListItemResponse,
    AppointmentListResponse,
    AppointmentStatusCountItem,
    AppointmentStatusUpdateRequest,
    AppointmentSummaryData,
    AppointmentTimeslotCountItem,
    AppointmentVisitTypeCountItem,
)
from app.models.appointment import Appointment


async def service_get_appointments(
    *,
    page: int,
    page_size: int,
    start_date: date | None = None,
    end_date: date | None = None,
    doctor_id: int | None = None,
    treatment_id: int | None = None,
    status: AppointmentStatus | None = None,
) -> AppointmentListResponse:
    """예약 목록 조회"""

    if page < 1 or page_size < 1 or page_size > 100:
        raise MediSolveAiException(ErrorMessages.INVALID_PAGINATION)

    start_datetime = _to_start_datetime(start_date)
    end_datetime = _to_end_datetime(end_date)

    async with get_async_session() as session:
        summaries, total_count = await Appointment.get_filtered(
            session=session,
            page=page,
            page_size=page_size,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        items = [_map_summary_to_response(summary) for summary in summaries]
        total_pages = _calculate_total_pages(total_count=total_count, page_size=page_size)

        return AppointmentListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total_count=total_count,
            total_pages=total_pages,
        )


async def service_update_appointment_status(
    appointment_id: int,
    request: AppointmentStatusUpdateRequest,
) -> AppointmentListItemResponse:
    """예약 상태 변경"""
    async with get_async_session() as session:
        appointment = await _get_appointment_or_raise(session=session, appointment_id=appointment_id)

        if appointment.status == request.status:
            return _map_appointment_to_response(appointment)

        if not appointment.can_transition_to(request.status):
            raise MediSolveAiException(ErrorMessages.APPOINTMENT_INVALID_STATUS_TRANSITION)

        await Appointment.update_status(session=session, appointment_id=appointment_id, status=request.status)
        await session.commit()
        await asyncio.gather(
            session.refresh(appointment),
            session.refresh(appointment.doctor),
            session.refresh(appointment.treatment),
            session.refresh(appointment.patient),
        )

        return _map_appointment_to_response(appointment)


async def service_get_appointment_status_counts(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    doctor_id: int | None = None,
    treatment_id: int | None = None,
    status: AppointmentStatus | None = None,
) -> list[AppointmentStatusCountItem]:
    start_datetime = _to_start_datetime(start_date)
    end_datetime = _to_end_datetime(end_date)

    async with get_async_session() as session:
        rows = await Appointment.get_status_counts(
            session=session,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )
        return [AppointmentStatusCountItem(status=row.status, count=row.count) for row in rows]


async def service_get_appointment_daily_counts(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    doctor_id: int | None = None,
    treatment_id: int | None = None,
    status: AppointmentStatus | None = None,
) -> list[AppointmentDailyCountItem]:
    start_datetime = _to_start_datetime(start_date)
    end_datetime = _to_end_datetime(end_date)

    async with get_async_session() as session:
        rows = await Appointment.get_daily_counts(
            session=session,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )
        return [AppointmentDailyCountItem(day=row.day, count=row.count) for row in rows]


async def service_get_appointment_timeslot_counts(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    doctor_id: int | None = None,
    treatment_id: int | None = None,
    status: AppointmentStatus | None = None,
) -> list[AppointmentTimeslotCountItem]:
    start_datetime = _to_start_datetime(start_date)
    end_datetime = _to_end_datetime(end_date)

    async with get_async_session() as session:
        rows = await Appointment.get_hourly_counts(
            session=session,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )
        return [AppointmentTimeslotCountItem(hour=row.hour, count=row.count) for row in rows]


async def service_get_appointment_visit_type_counts(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    doctor_id: int | None = None,
    treatment_id: int | None = None,
    status: AppointmentStatus | None = None,
) -> list[AppointmentVisitTypeCountItem]:
    start_datetime = _to_start_datetime(start_date)
    end_datetime = _to_end_datetime(end_date)

    async with get_async_session() as session:
        rows = await Appointment.get_visit_type_counts(
            session=session,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )
        return [AppointmentVisitTypeCountItem(visit_type=row.visit_type, count=row.count) for row in rows]


def _to_start_datetime(target_date: date | None) -> datetime | None:
    if target_date is None:
        return None
    return datetime.combine(target_date, time.min)


def _to_end_datetime(target_date: date | None) -> datetime | None:
    if target_date is None:
        return None
    return datetime.combine(target_date, time.max)


def _map_summary_to_response(summary: AppointmentSummaryData) -> AppointmentListItemResponse:
    return AppointmentListItemResponse(
        id=summary.id,
        appointment_datetime=summary.appointment_datetime,
        status=summary.status,
        visit_type=summary.visit_type,
        memo=summary.memo,
        doctor_id=summary.doctor_id,
        doctor_name=summary.doctor_name,
        treatment_id=summary.treatment_id,
        treatment_name=summary.treatment_name,
        treatment_duration_minutes=summary.treatment_duration_minutes,
        patient_id=summary.patient_id,
        patient_name=summary.patient_name,
        patient_phone=summary.patient_phone,
    )


def _map_appointment_to_response(appointment: Appointment) -> AppointmentListItemResponse:
    return AppointmentListItemResponse(
        id=appointment.id,
        appointment_datetime=appointment.appointment_datetime,
        status=appointment.status,
        visit_type=appointment.visit_type,
        memo=appointment.memo,
        doctor_id=appointment.doctor_id,
        doctor_name=appointment.doctor.name,
        treatment_id=appointment.treatment_id,
        treatment_name=appointment.treatment.name,
        treatment_duration_minutes=appointment.treatment.duration_minutes,
        patient_id=appointment.patient_id,
        patient_name=appointment.patient.name,
        patient_phone=appointment.patient.phone,
    )


def _calculate_total_pages(*, total_count: int, page_size: int) -> int:
    if total_count == 0:
        return 0
    return (total_count + page_size - 1) // page_size


async def _get_appointment_or_raise(session: AsyncSession, appointment_id: int) -> Appointment:
    appointment = await Appointment.get_by_id(session=session, appointment_id=appointment_id)
    if appointment is None:
        raise MediSolveAiException(ErrorMessages.APPOINTMENT_NOT_FOUND)
    return appointment
