"""
Doctor Mother

의사 테스트 데이터 생성용 클래스
"""

from __future__ import annotations

from app.core.constants import Department
from app.core.database.connection_async import get_async_session
from app.models.doctor import Doctor
from app.services.doctor_service import service_create_doctor


class DoctorMother:
    """의사 테스트 데이터 생성 클래스"""

    @staticmethod
    async def create(
        name: str = "홍길동",
        department: Department | str = Department.DERMATOLOGY,
        is_active: bool = True,
    ) -> Doctor:
        """
        의사 생성
        Args:
            name: 의사 이름 (기본값: "홍길동")
            department: 진료과 (기본값: Department.DERMATOLOGY)
            is_active: 활성 상태 (기본값: True)

        Returns:
            생성된 의사 객체
        """
        # StrEnum은 문자열로 자동 변환되므로 직접 사용 가능
        return await service_create_doctor(name=name, department=str(department), is_active=is_active)

    @staticmethod
    async def create_bulk(
        doctors_data: list[dict[str, str | bool]] | None = None,
        count: int = 3,
        department: Department | str = Department.DERMATOLOGY,
        is_active: bool = True,
    ) -> list[Doctor]:
        """
        의사 일괄 생성
        Args:
            doctors_data: 의사 데이터 리스트 (None이면 기본 데이터로 count만큼 생성)
            count: 생성할 의사 수 (기본값: 3)
            department: 진료과 (기본값: Department.DERMATOLOGY)
            is_active: 활성 상태 (기본값: True)

        Returns:
            생성된 의사 객체 리스트
        """
        # StrEnum은 문자열로 자동 변환되므로 직접 사용 가능
        department_str = str(department)
        if doctors_data is None:
            doctors_data = [
                {"name": f"의사{i+1}", "department": department_str, "is_active": is_active} for i in range(count)
            ]
        else:
            # doctors_data의 department도 StrEnum이면 문자열로 자동 변환
            for data in doctors_data:
                if "department" in data:
                    data["department"] = str(data["department"])

        async with get_async_session() as session:
            doctors = await Doctor.create_bulk(session=session, doctors_data=doctors_data)
            await session.commit()
            return doctors
