"""Admin Treatment Mother"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from app.tests.test_client import MediSolveAiAdminClient


class TreatmentMother:
    """진료 항목 테스트 데이터 생성 헬퍼"""

    def __init__(self, admin_client: MediSolveAiAdminClient) -> None:
        self._admin_client = admin_client

    async def create(
        self,
        *,
        name: str = "기본 진료",
        duration_minutes: int = 30,
        price: Decimal | float | str = Decimal("50000.00"),
        description: str | None = None,
        is_active: bool = True,
    ) -> dict[str, Any]:
        response = await self._admin_client.create_treatment(
            name=name,
            duration_minutes=duration_minutes,
            price=str(price),
            description=description,
            is_active=is_active,
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def create_bulk(
        self,
        count: int = 3,
        *,
        base_name: str = "Treatment",
        duration_minutes: int = 30,
        price: Decimal | float | str = Decimal("50000.00"),
        description: str | None = None,
        is_active: bool = True,
    ) -> list[dict[str, Any]]:
        treatments: list[dict[str, Any]] = []
        for idx in range(count):
            treatment = await self.create(
                name=f"{base_name} {idx}",
                duration_minutes=duration_minutes,
                price=price,
                description=description,
                is_active=is_active,
            )
            treatments.append(treatment)
        return treatments
