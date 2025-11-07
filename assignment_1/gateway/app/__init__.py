"""API Gateway 애플리케이션"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.core import settings

from .middleware.cors import add_cors_middleware
from .middleware.logging import LoggingMiddleware
from .routers.proxy import router as proxy_router

# FastAPI 앱 생성
app = FastAPI(
    title="Hospital Management Gateway",
    description="피부과 예약 관리 시스템 API Gateway",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 설정을 앱 상태에 저장
app.state.settings = settings

# 미들웨어 추가
add_cors_middleware(app)
app.add_middleware(LoggingMiddleware)

# 라우터 등록
app.include_router(proxy_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, Any]:
    """Gateway 루트 엔드포인트"""
    return {
        "service": "Hospital Management Gateway",
        "status": "running",
        "environment": settings.environment.value,
        "services": {
            "patient_api": f"http://localhost:{settings.patient_api_port}",
            "admin_api": f"http://localhost:{settings.admin_api_port}",
        },
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "gateway", "environment": settings.environment.value}
