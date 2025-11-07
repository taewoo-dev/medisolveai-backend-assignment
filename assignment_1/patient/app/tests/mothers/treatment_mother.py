"""
Treatment Mother

진료 항목 테스트 데이터 생성용 클래스
"""

from __future__ import annotations

from decimal import Decimal

from app.core.database.connection_async import get_async_session
from app.models.treatment import Treatment


class TreatmentMother:
    """진료 항목 테스트 데이터 생성 클래스"""

    @staticmethod
    async def create(
        name: str = "기본 진료",
        duration_minutes: int = 30,
        price: Decimal = Decimal("50000.00"),
        description: str | None = None,
        is_active: bool = True,
    ) -> Treatment:
        """
        진료 항목 생성
        Args:
            name: 진료 항목명 (기본값: "기본 진료")
            duration_minutes: 소요 시간(분) (기본값: 30)
            price: 가격 (기본값: 50000.00)
            description: 설명 (기본값: None)
            is_active: 활성 상태 (기본값: True)

        Returns:
            생성된 진료 항목 객체
        """
        async with get_async_session() as session:
            treatment = Treatment(
                name=name,
                duration_minutes=duration_minutes,
                price=price,
                description=description,
                is_active=is_active,
            )
            session.add(treatment)
            await session.flush()
            await session.refresh(treatment)
            await session.commit()
            return treatment
