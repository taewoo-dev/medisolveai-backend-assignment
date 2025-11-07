"""Patient App 통합 테스트"""

from __future__ import annotations

from .test_client import MediSolveAiPatientClient


async def test_patient_app_status(medisolveai_patient_client: MediSolveAiPatientClient) -> None:
    """Patient App 상태 확인 테스트"""
    response = await medisolveai_patient_client.get_status()
    assert "Hospital Management" in response["service"]
    assert "Patient API" in response["service"]
    assert response["status"] == "running"


async def test_patient_app_health(medisolveai_patient_client: MediSolveAiPatientClient) -> None:
    """Patient App 헬스 체크 테스트"""
    response = await medisolveai_patient_client.get_health()
    assert response["status"] == "healthy"
    assert response["service"] == "patient_api"
    assert "environment" in response
