"""Admin Treatment API Router"""

from __future__ import annotations

from fastapi import APIRouter, Path, Query, status

from app.dtos.treatment import (
    TreatmentCreateRequest,
    TreatmentResponse,
    TreatmentUpdateRequest,
)
from app.services import (
    service_create_treatment,
    service_delete_treatment,
    service_get_treatments,
    service_update_treatment,
)

router = APIRouter(prefix="/treatments", tags=["admin-treatments"])


@router.post(
    "",
    response_model=TreatmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="진료 항목 생성",
)
async def api_create_treatment(request: TreatmentCreateRequest) -> TreatmentResponse:
    """진료 항목을 생성합니다."""
    return await service_create_treatment(request=request)


@router.get(
    "",
    response_model=list[TreatmentResponse],
    status_code=status.HTTP_200_OK,
    summary="진료 항목 목록 조회",
)
async def api_get_treatments(
    is_active: bool | None = Query(None, description="활성 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
) -> list[TreatmentResponse]:
    """진료 항목 목록을 조회합니다."""
    return await service_get_treatments(
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{treatment_id}",
    response_model=TreatmentResponse,
    status_code=status.HTTP_200_OK,
    summary="진료 항목 수정",
)
async def api_update_treatment(
    request: TreatmentUpdateRequest,
    treatment_id: int = Path(..., description="진료 항목 ID"),
) -> TreatmentResponse:
    """진료 항목을 수정합니다."""

    return await service_update_treatment(treatment_id=treatment_id, request=request)


@router.delete(
    "/{treatment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="진료 항목 비활성화",
)
async def api_delete_treatment(
    treatment_id: int = Path(..., description="진료 항목 ID"),
) -> None:
    """진료 항목을 비활성화합니다."""
    await service_delete_treatment(treatment_id=treatment_id)
