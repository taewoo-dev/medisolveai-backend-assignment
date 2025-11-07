"""
데이터베이스 테이블 클린업 유틸리티

테스트 시 중복 데이터로 인한 충돌 방지를 위한 테이블 초기화 함수
"""

from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Appointment, Doctor, HospitalSlot, Patient, Treatment


async def reset_test_tables(session: AsyncSession) -> None:
    """
    테스트 테이블 초기화 함수
    테스트 시 중복 데이터로 인한 충돌 방지를 위해 사용
    외래키 제약조건을 고려하여 삭제 순서 중요

    Args:
        session: 데이터베이스 세션
    """
    # 외래키가 있는 테이블부터 삭제
    await session.execute(delete(Appointment))
    # 외래키가 없는 테이블 삭제
    await session.execute(delete(Doctor))
    await session.execute(delete(Patient))
    await session.execute(delete(Treatment))
    await session.execute(delete(HospitalSlot))
    await session.commit()
