"""Patient App pytest 설정 및 픽스처"""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import patch

import httpx
import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import app
from app.core.configs.settings import settings
from app.tests.test_client import MediSolveAiPatientClient
from app.tests.utils import reset_test_tables


@pytest.fixture()
def session_maker_medisolveai() -> async_sessionmaker[AsyncSession]:
    """테스트용 세션 메이커"""
    async_engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.is_local,
    )
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=async_engine,
    )


@pytest.fixture()
async def medisolveai_patient_client(
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[MediSolveAiPatientClient, None]:
    """Patient App 테스트 클라이언트 (DB 모킹 포함)"""
    with patch("app.core.database.connection_async.get_async_session", lambda: session_maker_medisolveai):
        # 테스트 전 테이블 초기화
        async with session_maker_medisolveai() as session:
            await reset_test_tables(session)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            yield MediSolveAiPatientClient(client)

        # 테스트 후 테이블 정리
        async with session_maker_medisolveai() as session:
            await reset_test_tables(session)
