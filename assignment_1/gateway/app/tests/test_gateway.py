"""Gateway 통합 테스트"""

from __future__ import annotations

import pytest

from .test_client import GatewayTestClient


@pytest.mark.asyncio
async def test_gateway_status(gateway_test_client: GatewayTestClient) -> None:
    """Gateway 상태 확인 테스트"""
    response = await gateway_test_client.get_status()
    assert "Hospital Management" in response["service"]
    assert "Gateway" in response["service"]
    assert response["status"] == "running"


@pytest.mark.asyncio
async def test_gateway_health(gateway_test_client: GatewayTestClient) -> None:
    """Gateway 헬스 체크 테스트"""
    response = await gateway_test_client.get_health()
    assert response["status"] == "healthy"
    assert response["service"] == "gateway"
    assert "environment" in response


@pytest.mark.asyncio
async def test_gateway_proxy_basic(gateway_test_client: GatewayTestClient) -> None:
    """Gateway 프록시 기본 테스트 (백엔드 서비스가 실행되지 않은 상태에서는 503 에러 예상)"""
    # Patient API 프록시 테스트
    patient_response = await gateway_test_client.proxy_patient_health()
    assert patient_response.status_code == 503  # Service Unavailable (백엔드 서비스 미실행)

    # Admin API 프록시 테스트
    admin_response = await gateway_test_client.proxy_admin_health()
    assert admin_response.status_code == 503  # Service Unavailable (백엔드 서비스 미실행)

    # 실제 프록시 테스트는 전체 서비스가 실행된 상태에서 수동으로 확인
