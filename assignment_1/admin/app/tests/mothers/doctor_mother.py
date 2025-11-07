"""Admin Doctor Mother"""

from __future__ import annotations

from typing import Any, cast

from app.core.constants import Department
from app.tests.test_client import MediSolveAiAdminClient


class DoctorMother:
    """의사 테스트 데이터 생성 헬퍼"""

    def __init__(self, admin_client: MediSolveAiAdminClient) -> None:
        self._admin_client = admin_client

    async def create(
        self,
        *,
        name: str = "Dr. Test",
        department: Department | str = Department.DERMATOLOGY,
        is_active: bool = True,
    ) -> dict[str, Any]:
        """단일 의사 레코드 생성 (API 호출)"""

        response = await self._admin_client.create_doctor(
            name=name,
            department=department,
            is_active=is_active,
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def create_bulk(
        self,
        count: int = 3,
        *,
        base_name: str = "Doctor",
        department: Department | str = Department.DERMATOLOGY,
        is_active: bool = True,
    ) -> list[dict[str, Any]]:
        """여러 의사를 일괄 생성 (API 호출)"""

        doctors: list[dict[str, Any]] = []
        for idx in range(count):
            doctor = await self.create(
                name=f"{base_name} {idx}",
                department=department,
                is_active=is_active,
            )
            doctors.append(doctor)
        return doctors
