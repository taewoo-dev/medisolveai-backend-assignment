"""Treatment CRUD Service"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.database.connection_async import get_async_session
from app.core.exceptions import MediSolveAiException
from app.dtos.treatment import (
    TreatmentCreateRequest,
    TreatmentResponse,
    TreatmentSummaryData,
    TreatmentUpdateRequest,
)
from app.models.treatment import Treatment

# ============================================================================
# 메인 서비스 함수
# ============================================================================


async def service_create_treatment(request: TreatmentCreateRequest) -> TreatmentResponse:
    """진료 항목 생성"""
    async with get_async_session() as session:
        treatment = await Treatment.create_one(
            session=session,
            name=request.name,
            duration_minutes=request.duration_minutes,
            price=request.price,
            description=request.description,
            is_active=request.is_active,
        )
        await session.commit()
        return _map_treatment_to_response(treatment)


async def service_get_treatments(
    *,
    is_active: bool | None = None,
    page: int = 1,
    page_size: int = 10,
) -> list[TreatmentResponse]:
    """진료 항목 목록 조회"""
    async with get_async_session() as session:
        offset = (page - 1) * page_size
        treatments = await Treatment.get_filtered(
            session=session,
            is_active=is_active,
            offset=offset,
            limit=page_size,
        )
        return [_map_treatment_summary_to_response(treatment) for treatment in treatments]


async def service_update_treatment(treatment_id: int, request: TreatmentUpdateRequest) -> TreatmentResponse:
    """진료 항목 수정"""

    if (
        request.name is None
        and request.duration_minutes is None
        and request.price is None
        and request.description is None
    ):
        raise MediSolveAiException(ErrorMessages.TREATMENT_UPDATE_EMPTY)

    async with get_async_session() as session:
        treatment = await _get_treatment_or_raise(session=session, treatment_id=treatment_id)

        await Treatment.update_fields(
            session=session,
            treatment_id=treatment_id,
            name=request.name,
            duration_minutes=request.duration_minutes,
            price=request.price,
            description=request.description,
        )

        await session.commit()

        if request.name is not None:
            treatment.name = request.name
        if request.duration_minutes is not None:
            treatment.duration_minutes = request.duration_minutes
        if request.price is not None:
            treatment.price = request.price
        if request.description is not None:
            treatment.description = request.description

        return _map_treatment_to_response(treatment)


async def service_delete_treatment(treatment_id: int) -> None:
    """진료 항목 비활성화"""
    async with get_async_session() as session:
        await _get_treatment_or_raise(session=session, treatment_id=treatment_id)

        await Treatment.set_active(session=session, treatment_id=treatment_id, is_active=False)
        await session.commit()


# ============================================================================
# 헬퍼 함수
# ============================================================================


def _map_treatment_to_response(treatment: Treatment) -> TreatmentResponse:
    return TreatmentResponse(
        id=treatment.id,
        name=treatment.name,
        duration_minutes=treatment.duration_minutes,
        price=treatment.price,
        description=treatment.description,
        is_active=treatment.is_active,
    )


def _map_treatment_summary_to_response(summary: TreatmentSummaryData) -> TreatmentResponse:
    return TreatmentResponse(
        id=summary.id,
        name=summary.name,
        duration_minutes=summary.duration_minutes,
        price=summary.price,
        description=None,
        is_active=summary.is_active,
    )


async def _get_treatment_or_raise(session: AsyncSession, treatment_id: int) -> Treatment:
    treatment = await Treatment.get_by_id(session=session, treatment_id=treatment_id)
    if treatment is None or not treatment.is_active:
        raise MediSolveAiException(ErrorMessages.TREATMENT_NOT_FOUND)
    return treatment
