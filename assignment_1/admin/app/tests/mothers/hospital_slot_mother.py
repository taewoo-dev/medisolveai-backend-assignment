"""Hospital Slot Mother"""

from __future__ import annotations

from typing import Any, cast

from app.tests.test_client import MediSolveAiAdminClient


class HospitalSlotMother:
    """병원 시간대 테스트 데이터 생성 헬퍼"""

    def __init__(self, admin_client: MediSolveAiAdminClient) -> None:
        self._admin_client = admin_client

    async def create(
        self,
        *,
        start_time: str = "09:00",
        end_time: str = "09:30",
        max_capacity: int = 3,
        is_active: bool = True,
    ) -> dict[str, Any]:
        """병원 시간대 생성 (API 호출)"""

        response = await self._admin_client.create_hospital_slot(
            start_time=start_time,
            end_time=end_time,
            max_capacity=max_capacity,
            is_active=is_active,
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
