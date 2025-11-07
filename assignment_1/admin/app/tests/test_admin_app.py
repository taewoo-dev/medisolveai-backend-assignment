"""Admin App 통합 테스트"""

from __future__ import annotations

from app.tests.test_client import MediSolveAiAdminClient


async def test_admin_app_status(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """Admin App 상태 확인 테스트"""
    response = await medisolveai_admin_client.get_status()
    assert "Hospital Management" in response["service"]
    assert "Admin API" in response["service"]
    assert response["status"] == "running"


async def test_admin_app_health(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """Admin App 헬스 체크 테스트"""
    response = await medisolveai_admin_client.get_health()
    assert response["status"] == "healthy"
    assert response["service"] == "admin_api"
    assert "environment" in response
