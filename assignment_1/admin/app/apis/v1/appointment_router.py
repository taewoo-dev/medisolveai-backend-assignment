"""Admin Appointment Router"""

from __future__ import annotations

import asyncio
from datetime import date

from fastapi import APIRouter, Path, Query, status

from app.core.constants.appointment_status import AppointmentStatus
from app.dtos import (
    AppointmentListItemResponse,
    AppointmentListResponse,
    AppointmentStatisticsResponse,
    AppointmentStatusUpdateRequest,
)
from app.services import (
    service_get_appointment_daily_counts,
    service_get_appointment_status_counts,
    service_get_appointment_timeslot_counts,
    service_get_appointment_visit_type_counts,
    service_get_appointments,
    service_update_appointment_status,
)

router = APIRouter(prefix="/appointments", tags=["Appointment"])


@router.get(
    "",
    response_model=AppointmentListResponse,
    summary="예약 목록 조회",
)
async def api_get_appointments(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(default=10, ge=1, le=100, description="페이지 크기"),
    start_date: date | None = Query(default=None, description="조회 시작일"),
    end_date: date | None = Query(default=None, description="조회 종료일"),
    doctor_id: int | None = Query(default=None, description="의사 ID"),
    treatment_id: int | None = Query(default=None, description="진료 항목 ID"),
    status: AppointmentStatus | None = Query(default=None, description="예약 상태"),
) -> AppointmentListResponse:
    """관리자용 예약 목록을 페이지네이션과 함께 조회합니다."""
    return await service_get_appointments(
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        doctor_id=doctor_id,
        treatment_id=treatment_id,
        status=status,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentListItemResponse,
    status_code=status.HTTP_200_OK,
    summary="예약 상태 변경",
)
async def api_update_appointment_status(
    request: AppointmentStatusUpdateRequest,
    appointment_id: int = Path(..., description="예약 ID"),
) -> AppointmentListItemResponse:
    """예약 상태를 변경합니다."""
    return await service_update_appointment_status(appointment_id=appointment_id, request=request)


@router.get(
    "/statistics",
    response_model=AppointmentStatisticsResponse,
    summary="예약 통계 조회",
)
async def api_get_appointment_statistics(
    start_date: date | None = Query(default=None, description="조회 시작일"),
    end_date: date | None = Query(default=None, description="조회 종료일"),
    doctor_id: int | None = Query(default=None, description="의사 ID"),
    treatment_id: int | None = Query(default=None, description="진료 항목 ID"),
    status: AppointmentStatus | None = Query(default=None, description="예약 상태"),
) -> AppointmentStatisticsResponse:
    """예약 통계를 조회합니다."""

    status_counts, daily_counts, timeslot_counts, visit_counts = await asyncio.gather(
        service_get_appointment_status_counts(
            start_date=start_date,
            end_date=end_date,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        ),
        service_get_appointment_daily_counts(
            start_date=start_date,
            end_date=end_date,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        ),
        service_get_appointment_timeslot_counts(
            start_date=start_date,
            end_date=end_date,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        ),
        service_get_appointment_visit_type_counts(
            start_date=start_date,
            end_date=end_date,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        ),
    )

    return AppointmentStatisticsResponse(
        status_counts=status_counts,
        daily_counts=daily_counts,
        timeslot_counts=timeslot_counts,
        visit_type_counts=visit_counts,
    )
