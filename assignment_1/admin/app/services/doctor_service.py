"""Doctor CRUD Service"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.database.connection_async import get_async_session
from app.core.exceptions import MediSolveAiException
from app.dtos.doctor import (
    DoctorCreateRequest,
    DoctorResponse,
    DoctorSummaryData,
    DoctorUpdateRequest,
)
from app.models.doctor import Doctor

# ============================================================================
# 메인 서비스 함수
# ============================================================================


async def service_create_doctor(request: DoctorCreateRequest) -> DoctorResponse:
    """의사 생성"""
    async with get_async_session() as session:
        doctor = await Doctor.create_one(
            session=session,
            name=request.name,
            department=request.department,
            is_active=request.is_active,
        )
        await session.commit()
        return _map_doctor_to_response(doctor)


async def service_get_doctors(
    department: str | None = None,
    is_active: bool | None = None,
    *,
    page: int = 1,
    page_size: int = 10,
) -> list[DoctorResponse]:
    """의사 목록 조회"""
    async with get_async_session() as session:
        offset = (page - 1) * page_size
        doctors = await Doctor.get_filtered(
            session=session,
            department=department,
            is_active=is_active,
            offset=offset,
            limit=page_size,
        )
        return [_map_summary_to_response(doctor) for doctor in doctors]


async def service_update_doctor(doctor_id: int, request: DoctorUpdateRequest) -> DoctorResponse:
    """의사 정보 수정"""

    if request.name is None and request.department is None:
        raise MediSolveAiException(ErrorMessages.DOCTOR_UPDATE_EMPTY)

    async with get_async_session() as session:
        doctor = await _get_doctor_or_raise(session=session, doctor_id=doctor_id)

        await Doctor.update_fields(
            session=session,
            doctor_id=doctor_id,
            name=request.name,
            department=request.department,
        )

        await session.commit()

        if request.name is not None:
            doctor.name = request.name
        if request.department is not None:
            doctor.department = request.department

        return _map_doctor_to_response(doctor)


async def service_delete_doctor(doctor_id: int) -> None:
    """의사 비활성화"""
    async with get_async_session() as session:
        await _get_doctor_or_raise(session=session, doctor_id=doctor_id)

        await Doctor.set_active(session=session, doctor_id=doctor_id, is_active=False)

        await session.commit()


# ============================================================================
# 헬퍼 함수
# ============================================================================


def _map_doctor_to_response(doctor: Doctor) -> DoctorResponse:
    """Doctor 모델을 응답 DTO로 변환"""
    return DoctorResponse(
        id=doctor.id,
        name=doctor.name,
        department=doctor.department,
        is_active=doctor.is_active,
    )


def _map_summary_to_response(summary: DoctorSummaryData) -> DoctorResponse:
    return DoctorResponse(
        id=summary.id,
        name=summary.name,
        department=summary.department,
        is_active=summary.is_active,
    )


async def _get_doctor_or_raise(session: AsyncSession, doctor_id: int) -> Doctor:
    doctor = await Doctor.get_by_id(session=session, doctor_id=doctor_id)
    if doctor is None or not doctor.is_active:
        raise MediSolveAiException(ErrorMessages.DOCTOR_NOT_FOUND)
    return doctor
