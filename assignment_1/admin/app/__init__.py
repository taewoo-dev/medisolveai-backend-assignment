"""Admin API 애플리케이션"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.apis.v1 import appointment_router, doctor_router, hospital_slot_router, treatment_router
from app.core import settings
from app.core.exceptions import MediSolveAiException

# FastAPI 앱 생성
app = FastAPI(
    title="Hospital Management Admin API",
    description="피부과 예약 관리 시스템 관리자용 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# 예외 핸들러 등록
@app.exception_handler(MediSolveAiException)
async def medi_solve_ai_exception_handler(request: Request, exc: MediSolveAiException) -> JSONResponse:
    """MediSolveAiException 예외 핸들러"""

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message, "details": exc.details},
    )


# 라우터 등록
app.include_router(doctor_router, prefix="/api/v1/admin")
app.include_router(treatment_router, prefix="/api/v1/admin")
app.include_router(hospital_slot_router, prefix="/api/v1/admin")
app.include_router(appointment_router, prefix="/api/v1/admin")


@app.get("/")
async def root() -> dict[str, Any]:
    """Admin API 루트 엔드포인트"""

    return {
        "service": "Hospital Management Admin API",
        "status": "running",
        "environment": settings.environment.value,
        "features": [
            "의사 관리",
            "진료 항목 관리",
            "병원 슬롯 관리",
            "예약 현황 관리",
            "통계 조회",
        ],
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """헬스체크 엔드포인트"""

    return {"status": "healthy", "service": "admin_api", "environment": settings.environment.value}
