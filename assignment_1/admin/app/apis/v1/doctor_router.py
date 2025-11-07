"""Admin Doctor API Router"""

from __future__ import annotations

from fastapi import APIRouter, Path, Query, status

from app.dtos.doctor import DoctorCreateRequest, DoctorResponse, DoctorUpdateRequest
from app.services import (
    service_create_doctor,
    service_delete_doctor,
    service_get_doctors,
    service_update_doctor,
)

router = APIRouter(prefix="/doctors", tags=["admin-doctors"])


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="의사 정보 생성",
)
async def api_create_doctor(request: DoctorCreateRequest) -> DoctorResponse:
    """의사 정보를 생성합니다."""
    return await service_create_doctor(request=request)


@router.get(
    "",
    response_model=list[DoctorResponse],
    status_code=status.HTTP_200_OK,
    summary="의사 목록 조회",
)
async def api_get_doctors(
    department: str | None = Query(None, description="진료과 필터"),
    is_active: bool | None = Query(None, description="활성 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
) -> list[DoctorResponse]:
    """의사 목록을 조회합니다."""
    return await service_get_doctors(
        department=department,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="의사 정보 수정",
)
async def api_update_doctor(
    request: DoctorUpdateRequest,
    doctor_id: int = Path(..., description="의사 ID"),
) -> DoctorResponse:
    """의사 정보를 수정합니다."""

    return await service_update_doctor(doctor_id=doctor_id, request=request)


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="의사 비활성화",
    description="의사를 비활성화합니다.",
)
async def api_delete_doctor(
    doctor_id: int = Path(..., description="의사 ID"),
) -> None:
    """의사 정보를 비활성화합니다."""
    await service_delete_doctor(doctor_id=doctor_id)
