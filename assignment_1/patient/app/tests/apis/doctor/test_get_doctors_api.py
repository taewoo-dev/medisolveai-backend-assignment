"""
의사 조회 API 테스트
"""

from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import Department
from app.tests.mothers import DoctorMother
from app.tests.test_client import MediSolveAiPatientClient


async def test_get_doctors_success(
    medisolveai_patient_client: MediSolveAiPatientClient, session_maker_medisolveai: async_sessionmaker[AsyncSession]
) -> None:
    """의사 목록 조회 성공 테스트"""
    # Given: 피부과 의사 3명 생성
    created_doctors = await DoctorMother.create_bulk(count=3, department=Department.DERMATOLOGY)

    # When: 의사 목록 조회
    response = await medisolveai_patient_client.get_doctors()
    doctors = response.json()

    # Then: 응답 검증
    assert response.status_code == 200
    assert isinstance(doctors, list)
    assert len(doctors) == 3

    # Then: 생성한 의사 정보가 정확히 일치하는지 검증
    assert doctors[0]["id"] == created_doctors[0].id
    assert doctors[0]["name"] == "의사1"
    assert doctors[0]["department"] == Department.DERMATOLOGY
    assert doctors[0]["is_active"] is True

    assert doctors[1]["id"] == created_doctors[1].id
    assert doctors[1]["name"] == "의사2"
    assert doctors[1]["department"] == Department.DERMATOLOGY
    assert doctors[1]["is_active"] is True

    assert doctors[2]["id"] == created_doctors[2].id
    assert doctors[2]["name"] == "의사3"
    assert doctors[2]["department"] == Department.DERMATOLOGY
    assert doctors[2]["is_active"] is True


async def test_get_doctors_with_department_filter(
    medisolveai_patient_client: MediSolveAiPatientClient, session_maker_medisolveai: async_sessionmaker[AsyncSession]
) -> None:
    """진료과 필터링으로 의사 목록 조회 테스트"""
    # Given: 피부과 의사 3명, 정형외과 의사 3명 생성 (병렬 처리)
    created_doctors_skin, _ = await asyncio.gather(
        DoctorMother.create_bulk(
            count=3,
            department=Department.DERMATOLOGY,
            doctors_data=[
                {"name": f"피부과의사{i+1}", "department": Department.DERMATOLOGY, "is_active": True} for i in range(3)
            ],
        ),
        DoctorMother.create_bulk(
            count=3,
            department=Department.ORTHOPEDICS,
            doctors_data=[
                {"name": f"정형외과의사{i+1}", "department": Department.ORTHOPEDICS, "is_active": True}
                for i in range(3)
            ],
        ),
    )

    # When: 피부과로 필터링하여 의사 목록 조회
    filtered_response = await medisolveai_patient_client.get_doctors(department=Department.DERMATOLOGY)
    filtered_doctors = filtered_response.json()

    # Then: 응답 검증
    assert filtered_response.status_code == 200
    assert isinstance(filtered_doctors, list)
    assert len(filtered_doctors) == 3

    # Then: 필터링된 의사들이 모두 피부과 의사인지 검증
    assert filtered_doctors[0]["id"] == created_doctors_skin[0].id
    assert filtered_doctors[0]["name"] == "피부과의사1"
    assert filtered_doctors[0]["department"] == Department.DERMATOLOGY
    assert filtered_doctors[0]["is_active"] is True

    assert filtered_doctors[1]["id"] == created_doctors_skin[1].id
    assert filtered_doctors[1]["name"] == "피부과의사2"
    assert filtered_doctors[1]["department"] == Department.DERMATOLOGY
    assert filtered_doctors[1]["is_active"] is True

    assert filtered_doctors[2]["id"] == created_doctors_skin[2].id
    assert filtered_doctors[2]["name"] == "피부과의사3"
    assert filtered_doctors[2]["department"] == Department.DERMATOLOGY
    assert filtered_doctors[2]["is_active"] is True


async def test_get_doctors_only_active(
    medisolveai_patient_client: MediSolveAiPatientClient, session_maker_medisolveai: async_sessionmaker[AsyncSession]
) -> None:
    """활성 상태인 의사만 조회되는지 확인"""
    # Given: 활성 의사 3명, 비활성 의사 3명 생성 (병렬 처리)
    created_doctors_active, _ = await asyncio.gather(
        DoctorMother.create_bulk(
            count=3,
            department=Department.DERMATOLOGY,
            is_active=True,
            doctors_data=[
                {"name": f"활성의사{i+1}", "department": Department.DERMATOLOGY, "is_active": True} for i in range(3)
            ],
        ),
        DoctorMother.create_bulk(
            count=3,
            department=Department.DERMATOLOGY,
            is_active=False,
            doctors_data=[
                {"name": f"비활성의사{i+1}", "department": Department.DERMATOLOGY, "is_active": False} for i in range(3)
            ],
        ),
    )

    # When: 의사 목록 조회
    response = await medisolveai_patient_client.get_doctors()
    doctors = response.json()

    # Then: 응답 검증
    assert response.status_code == 200
    assert isinstance(doctors, list)
    assert len(doctors) == 3

    # Then: 활성 상태인 의사만 조회되는지 검증
    assert doctors[0]["id"] == created_doctors_active[0].id
    assert doctors[0]["name"] == "활성의사1"
    assert doctors[0]["department"] == Department.DERMATOLOGY
    assert doctors[0]["is_active"] is True

    assert doctors[1]["id"] == created_doctors_active[1].id
    assert doctors[1]["name"] == "활성의사2"
    assert doctors[1]["department"] == Department.DERMATOLOGY
    assert doctors[1]["is_active"] is True

    assert doctors[2]["id"] == created_doctors_active[2].id
    assert doctors[2]["name"] == "활성의사3"
    assert doctors[2]["department"] == Department.DERMATOLOGY
    assert doctors[2]["is_active"] is True
