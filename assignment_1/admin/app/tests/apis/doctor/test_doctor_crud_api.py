"""Admin Doctor CRUD API 테스트"""

from __future__ import annotations

import asyncio

from app.core.constants import Department, ErrorMessages
from app.tests.mothers import DoctorMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_create_doctor_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """의사 생성 성공"""

    # When: 의사 생성
    response = await medisolveai_admin_client.create_doctor(
        name="Dr. Kim",
        department=Department.DERMATOLOGY,
    )

    # Then: 생성 결과 검증
    assert response.status_code == 201

    doctor = response.json()
    assert doctor["name"] == "Dr. Kim"
    assert doctor["department"] == Department.DERMATOLOGY
    assert doctor["is_active"] is True


async def test_get_doctors_with_filters(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """의사 목록 조회 - 필터 적용"""

    # Given: 서로 다른 상태의 의사 생성
    mother = DoctorMother(medisolveai_admin_client)
    await asyncio.gather(
        mother.create(name="Dr. Kim", department=Department.DERMATOLOGY),
        mother.create(name="Dr. Lee", department=Department.SURGERY, is_active=False),
    )

    # When: 특정 진료과 및 활성 상태로 조회
    response, response_inactive = await asyncio.gather(
        medisolveai_admin_client.get_doctors(department=Department.DERMATOLOGY),
        medisolveai_admin_client.get_doctors(is_active=False),
    )

    # Then: 진료과 필터 결과 검증
    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) == 1
    assert doctors[0]["department"] == Department.DERMATOLOGY

    assert response_inactive.status_code == 200
    doctors_inactive = response_inactive.json()
    assert len(doctors_inactive) == 1
    assert doctors_inactive[0]["is_active"] is False


async def test_update_doctor_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """의사 정보 수정 성공"""

    mother = DoctorMother(medisolveai_admin_client)

    # Given: 기존 의사 생성
    doctor = await mother.create(name="Dr. Kim", department=Department.DERMATOLOGY)

    # When: 의사 이름과 진료과 수정
    response = await medisolveai_admin_client.update_doctor(
        doctor["id"],
        name="Dr. Kim Updated",
        department=Department.SURGERY,
    )

    # Then: 응답 코드 확인 (200)
    assert response.status_code == 200
    updated_doctor = response.json()
    assert updated_doctor["name"] == "Dr. Kim Updated"
    assert updated_doctor["department"] == Department.SURGERY
    assert updated_doctor["is_active"] is True


async def test_update_doctor_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 의사 수정 시 예외"""

    # When: 존재하지 않는 의사 수정 시도
    response = await medisolveai_admin_client.update_doctor(9999, name="Unknown")

    # Then: 에러 응답 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.DOCTOR_NOT_FOUND


async def test_delete_doctor_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """의사 비활성화 성공"""

    mother = DoctorMother(medisolveai_admin_client)

    # Given: 기존 의사 생성
    doctor = await mother.create(name="Dr. Kim", department=Department.DERMATOLOGY)

    # When: 의사 비활성화
    delete_response = await medisolveai_admin_client.delete_doctor(doctor["id"])
    inactive_response, active_response = await asyncio.gather(
        medisolveai_admin_client.get_doctors(is_active=False),
        medisolveai_admin_client.get_doctors(is_active=True),
    )

    # Then: 비활성화 결과 검증
    assert delete_response.status_code == 204
    inactive_items = inactive_response.json()
    assert any(item["id"] == doctor["id"] for item in inactive_items)
    active_items = active_response.json()
    assert all(item["id"] != doctor["id"] for item in active_items)


async def test_delete_doctor_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 의사 삭제 시 예외"""

    # When: 존재하지 않는 의사 삭제 시도
    response = await medisolveai_admin_client.delete_doctor(9999)

    # Then: 에러 응답 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.DOCTOR_NOT_FOUND


async def test_get_doctors_pagination(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """의사 목록 조회 - 페이지네이션"""

    mother = DoctorMother(medisolveai_admin_client)

    # Given: 총 12명의 의사 생성 (10+2)
    await mother.create_bulk(count=12, base_name="Doctor", department=Department.DERMATOLOGY)

    # When: 첫 페이지 조회
    page1_response = await medisolveai_admin_client.get_doctors()

    # Then: 첫 페이지 결과 검증
    assert page1_response.status_code == 200
    page1_doctors = page1_response.json()
    assert len(page1_doctors) == 10
    assert page1_doctors[0]["name"] == "Doctor 0"
    assert page1_doctors[-1]["name"] == "Doctor 9"

    # When: 두 번째 페이지 조회
    page2_response = await medisolveai_admin_client.get_doctors(page=2)

    # Then: 두 번째 페이지 결과 검증
    assert page2_response.status_code == 200
    page2_doctors = page2_response.json()
    assert len(page2_doctors) == 2
    assert page2_doctors[0]["name"] == "Doctor 10"
    assert page2_doctors[1]["name"] == "Doctor 11"
