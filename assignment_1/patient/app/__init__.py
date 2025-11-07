"""Patient API 애플리케이션"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.apis.v1.appointment_router import router as appointment_router
from app.apis.v1.doctor_router import router as doctor_router
from app.core import settings
from app.core.exceptions import MediSolveAiException

# FastAPI 앱 생성
app = FastAPI(
    title="Hospital Management Patient API",
    description="피부과 예약 관리 시스템 환자용 API",
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
app.include_router(doctor_router, prefix="/api/v1/patient")
app.include_router(appointment_router, prefix="/api/v1/patient/appointments")


@app.get("/")
async def root() -> dict[str, Any]:
    """Patient API 루트 엔드포인트"""
    return {
        "service": "Hospital Management Patient API",
        "status": "running",
        "environment": settings.environment.value,
        "features": ["의사 조회", "예약 생성", "예약 조회", "예약 취소"],
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "patient_api", "environment": settings.environment.value}
