"""Gateway 전용 테스트 클라이언트"""

from __future__ import annotations

from typing import Any

import httpx


class GatewayTestClient:
    """Gateway 테스트 클라이언트"""

    def __init__(self, httpx_client: httpx.AsyncClient):
        """
        Gateway 테스트 중 API 호출은 본 클래스를 통합니다.
        """
        self._client = httpx_client

    async def get_status(self) -> dict[str, Any]:
        """Gateway 상태 확인"""
        response = await self._client.get("/")
        return dict(response.json())

    async def get_health(self) -> dict[str, Any]:
        """Gateway 헬스 체크"""
        response = await self._client.get("/health")
        return dict(response.json())

    # 프록시 테스트 메서드들
    async def proxy_patient_health(self) -> httpx.Response:
        """Patient API 프록시 헬스 체크"""
        return await self._client.get("/api/v1/patient/health")

    async def proxy_admin_health(self) -> httpx.Response:
        """Admin API 프록시 헬스 체크"""
        return await self._client.get("/api/v1/admin/health")

    async def proxy_patient_status(self) -> httpx.Response:
        """Patient API 프록시 상태 확인"""
        return await self._client.get("/api/v1/patient")

    async def proxy_admin_status(self) -> httpx.Response:
        """Admin API 프록시 상태 확인"""
        return await self._client.get("/api/v1/admin")
