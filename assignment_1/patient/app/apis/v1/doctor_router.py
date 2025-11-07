"""
Doctor Router

의사 정보 조회 API
"""

from fastapi import APIRouter, Query

from app.dtos.doctor import DoctorResponse
from app.services.doctor_service import service_get_doctors

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorResponse])
async def api_get_doctors(department: str | None = Query(None, description="진료과 필터")) -> list[DoctorResponse]:
    """
    의사 목록 조회
    - 활성 상태인 의사만 조회
    - 진료과로 필터링 가능 (옵션)
    - 이름 순으로 정렬
    """
    return await service_get_doctors(department=department)
