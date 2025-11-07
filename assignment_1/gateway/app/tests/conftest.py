"""Gateway pytest 설정 및 픽스처"""

from __future__ import annotations

from typing import AsyncGenerator

import httpx
import pytest

from .test_client import GatewayTestClient


@pytest.fixture()
async def gateway_test_client() -> AsyncGenerator[GatewayTestClient, None]:
    """Gateway 테스트 클라이언트"""

    # Gateway App import
    from app import app as gateway_app

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway_app), base_url="http://test") as client:
        yield GatewayTestClient(client)
