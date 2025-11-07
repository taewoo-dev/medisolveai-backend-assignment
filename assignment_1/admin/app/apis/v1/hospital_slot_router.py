"""Admin Hospital Slot Router"""

from __future__ import annotations

from fastapi import APIRouter, Path, Query, status

from app.dtos import (
    HospitalSlotCreateRequest,
    HospitalSlotResponse,
    HospitalSlotUpdateRequest,
)
from app.services import (
    service_create_hospital_slot,
    service_delete_hospital_slot,
    service_get_hospital_slots,
    service_update_hospital_slot,
)

router = APIRouter(prefix="/hospital-slots", tags=["Hospital Slot"])


@router.get("", response_model=list[HospitalSlotResponse], summary="병원 시간대 목록 조회")
async def api_get_hospital_slots(
    is_active: bool | None = Query(default=None, description="활성 여부 필터"),
) -> list[HospitalSlotResponse]:
    """병원 시간대를 조회합니다."""
    return await service_get_hospital_slots(is_active=is_active)


@router.post(
    "",
    response_model=HospitalSlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="병원 시간대 생성",
)
async def api_create_hospital_slot(
    request: HospitalSlotCreateRequest,
) -> HospitalSlotResponse:
    """병원 시간대를 생성합니다."""
    return await service_create_hospital_slot(request=request)


@router.patch(
    "/{slot_id}",
    response_model=HospitalSlotResponse,
    status_code=status.HTTP_200_OK,
    summary="병원 시간대 수정",
)
async def api_update_hospital_slot(
    request: HospitalSlotUpdateRequest,
    slot_id: int = Path(..., description="슬롯 ID"),
) -> HospitalSlotResponse:
    """병원 시간대를 수정합니다."""
    return await service_update_hospital_slot(slot_id=slot_id, request=request)


@router.delete(
    "/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="병원 시간대 비활성화",
)
async def api_delete_hospital_slot(
    slot_id: int = Path(..., description="슬롯 ID"),
) -> None:
    """병원 시간대를 비활성화합니다."""
    await service_delete_hospital_slot(slot_id=slot_id)
