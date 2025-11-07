"""
Appointment Router

예약 관련 API 엔드포인트
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Path, Query, status

from app.dtos.appointment import (
    AppointmentResponse,
    AvailableTimeResponse,
    CreateAppointmentRequest,
)
from app.services.appointment_service import (
    service_cancel_appointment,
    service_create_appointment,
    service_get_appointments,
    service_get_available_times,
)

router = APIRouter(tags=["appointments"])


@router.get(
    "/available-times",
    response_model=AvailableTimeResponse,
    status_code=status.HTTP_200_OK,
    summary="예약 가능 시간 조회",
    description="특정 의사의 예약 가능한 시간대를 조회합니다.",
)
async def api_get_available_times(
    doctor_id: int = Query(..., description="의사 ID"),
    treatment_id: int = Query(..., description="진료 항목 ID"),
    appointment_date: date = Query(..., alias="date", description="조회할 날짜 (YYYY-MM-DD)"),
) -> AvailableTimeResponse:
    """예약 가능 시간 조회 API"""
    return await service_get_available_times(
        doctor_id=doctor_id, treatment_id=treatment_id, appointment_date=appointment_date
    )


@router.get(
    "",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="예약 목록 조회",
    description="환자 본인의 예약 목록을 조회합니다.",
)
async def api_get_appointments(
    patient_phone: str = Query(..., description="환자 전화번호"),
) -> list[AppointmentResponse]:
    """예약 목록 조회 API"""
    return await service_get_appointments(patient_phone=patient_phone)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="예약 생성",
    description="새로운 예약을 생성합니다.",
)
async def api_create_appointment(request: CreateAppointmentRequest) -> AppointmentResponse:
    """예약 생성 API"""
    return await service_create_appointment(request=request)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="예약 취소",
    description="예약을 취소 상태로 변경합니다.",
)
async def api_cancel_appointment(
    appointment_id: int = Path(..., description="예약 ID"),
    patient_phone: str = Query(..., description="환자 전화번호"),
) -> AppointmentResponse:
    """예약 취소 API"""
    return await service_cancel_appointment(appointment_id=appointment_id, patient_phone=patient_phone)
