"""Hospital Slot Service"""

from __future__ import annotations

from datetime import datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.database.connection_async import get_async_session
from app.core.exceptions import MediSolveAiException
from app.dtos.hospital_slot import (
    HospitalSlotCreateRequest,
    HospitalSlotResponse,
    HospitalSlotSummaryData,
    HospitalSlotUpdateRequest,
)
from app.models.hospital_slot import HospitalSlot

# ============================================================================
# 메인 서비스 함수
# ============================================================================


async def service_create_hospital_slot(request: HospitalSlotCreateRequest) -> HospitalSlotResponse:
    """병원 시간대 생성"""
    async with get_async_session() as session:
        _validate_slot_interval(start_time=request.start_time, end_time=request.end_time)
        await _ensure_unique_slot(session=session, start_time=request.start_time, end_time=request.end_time)

        slot = await HospitalSlot.create_one(
            session=session,
            start_time=request.start_time,
            end_time=request.end_time,
            max_capacity=request.max_capacity,
            is_active=request.is_active,
        )
        await session.commit()
        return _map_slot_to_response(slot)


async def service_get_hospital_slots(
    *,
    is_active: bool | None = None,
) -> list[HospitalSlotResponse]:
    """병원 시간대 목록 조회"""

    async with get_async_session() as session:
        slots = await HospitalSlot.get_filtered(session=session, is_active=is_active)
        return [_map_summary_to_response(slot) for slot in slots]


async def service_update_hospital_slot(
    slot_id: int,
    request: HospitalSlotUpdateRequest,
) -> HospitalSlotResponse:
    """병원 시간대 수정"""
    async with get_async_session() as session:
        slot = await _get_slot_or_raise(session=session, slot_id=slot_id)
        await HospitalSlot.update_max_capacity(
            session=session,
            slot_id=slot_id,
            max_capacity=request.max_capacity,
        )

        await session.commit()
        await session.refresh(slot)

        return _map_slot_to_response(slot)


async def service_delete_hospital_slot(slot_id: int) -> None:
    """병원 시간대 비활성화"""
    async with get_async_session() as session:
        slot = await _get_slot_or_raise(session=session, slot_id=slot_id)

        if not slot.is_active:
            raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_NOT_FOUND)

        await HospitalSlot.set_active(session=session, slot_id=slot_id, is_active=False)
        await session.commit()


# ============================================================================
# 헬퍼 함수
# ============================================================================


def _map_slot_to_response(slot: HospitalSlot) -> HospitalSlotResponse:
    return HospitalSlotResponse(
        id=slot.id,
        start_time=slot.start_time,
        end_time=slot.end_time,
        max_capacity=slot.max_capacity,
        is_active=slot.is_active,
    )


def _map_summary_to_response(summary: HospitalSlotSummaryData) -> HospitalSlotResponse:
    return HospitalSlotResponse(
        id=summary.id,
        start_time=summary.start_time,
        end_time=summary.end_time,
        max_capacity=summary.max_capacity,
        is_active=summary.is_active,
    )


async def _get_slot_or_raise(session: AsyncSession, slot_id: int) -> HospitalSlot:
    slot = await HospitalSlot.get_by_id(session=session, slot_id=slot_id)
    if slot is None:
        raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_NOT_FOUND)
    return slot


async def _ensure_unique_slot(
    *,
    session: AsyncSession,
    start_time: time,
    end_time: time,
    exclude_slot_id: int | None = None,
) -> None:
    existing = await HospitalSlot.get_by_time(session=session, start_time=start_time, end_time=end_time)
    if existing is not None and existing.id != exclude_slot_id:
        raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_TIME_CONFLICT)


def _validate_slot_interval(*, start_time: time, end_time: time) -> None:
    if end_time <= start_time:
        raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_INVALID_INTERVAL)

    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    diff = end_dt - start_dt

    if diff != timedelta(minutes=30):
        raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_INVALID_INTERVAL)

    if start_time.minute not in {0, 30} or end_time.minute not in {0, 30}:
        raise MediSolveAiException(ErrorMessages.HOSPITAL_SLOT_INVALID_INTERVAL)
