"""Admin Treatment CRUD API 테스트"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from app.core.constants import ErrorMessages
from app.tests.mothers import TreatmentMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_create_treatment_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """진료 항목 생성 성공"""

    # When: 진료 항목 생성
    response = await medisolveai_admin_client.create_treatment(
        name="기본 진료",
        duration_minutes=30,
        price="50000.00",
        description="기본 검사",
    )

    # Then: 생성 결과 검증
    assert response.status_code == 201
    treatment = response.json()
    assert treatment["name"] == "기본 진료"
    assert treatment["duration_minutes"] == 30
    assert treatment["price"] == "50000.00"
    assert treatment["description"] == "기본 검사"
    assert treatment["is_active"] is True


async def test_create_treatment_invalid_duration(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """30분 단위가 아닌 소요 시간은 생성 실패"""

    # When: 45분 소요 시간으로 생성 요청
    response = await medisolveai_admin_client.create_treatment(
        name="비정상 진료",
        duration_minutes=45,
        price="50000.00",
    )

    # Then: 422 응답 확인
    assert response.status_code == 422


async def test_get_treatments_with_filters(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """진료 항목 목록 조회 - 활성 여부 필터"""

    treatment_mother = TreatmentMother(medisolveai_admin_client)

    # Given: 활성/비활성 진료 항목 생성
    await asyncio.gather(
        treatment_mother.create(name="활성 진료", is_active=True),
        treatment_mother.create(name="비활성 진료", is_active=False),
    )

    # When: 활성/비활성 진료 항목 조회
    response_active, response_inactive = await asyncio.gather(
        medisolveai_admin_client.get_treatments(is_active=True),
        medisolveai_admin_client.get_treatments(is_active=False),
    )

    # Then: 활성 항목만 반환되는지 검증
    assert response_active.status_code == 200
    active_items = response_active.json()
    assert len(active_items) == 1
    assert active_items[0]["name"] == "활성 진료"

    # Then: 비활성 항목만 반환되는지 검증
    assert response_inactive.status_code == 200
    inactive_items = response_inactive.json()
    assert len(inactive_items) == 1
    assert inactive_items[0]["name"] == "비활성 진료"


async def test_update_treatment_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """진료 항목 수정 성공"""

    treatment_mother = TreatmentMother(medisolveai_admin_client)

    # Given: 기존 진료 항목 생성
    treatment = await treatment_mother.create(name="기존 진료", duration_minutes=30, price=Decimal("50000.00"))

    # When: 진료 항목 정보 수정
    response = await medisolveai_admin_client.update_treatment(
        treatment["id"],
        name="수정 진료",
        duration_minutes=60,
        price="75000.00",
    )

    # Then: 응답 코드 확인 (200)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "수정 진료"
    assert updated["duration_minutes"] == 60
    assert updated["price"] == "75000.00"


async def test_update_treatment_invalid_duration(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """30분 단위가 아닌 소요 시간 수정 실패"""

    treatment_mother = TreatmentMother(medisolveai_admin_client)

    # Given: 기존 진료 항목 생성
    treatment = await treatment_mother.create(name="갱신 대상", duration_minutes=30, price="50000.00")

    # When: 45분으로 수정 시도
    response = await medisolveai_admin_client.update_treatment(treatment["id"], duration_minutes=45)

    # Then: 422 응답 확인
    assert response.status_code == 422


async def test_update_treatment_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 진료 항목 수정 시 예외"""

    # When: 존재하지 않는 ID로 수정 시도
    response = await medisolveai_admin_client.update_treatment(9999, name="Unknown")

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.TREATMENT_NOT_FOUND


async def test_delete_treatment_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """진료 항목 비활성화 성공"""

    treatment_mother = TreatmentMother(medisolveai_admin_client)

    # Given: 기존 진료 항목 생성
    treatment = await treatment_mother.create(name="삭제 대상", duration_minutes=30, price=Decimal("50000.00"))

    # When: 진료 항목 비활성화
    delete_response = await medisolveai_admin_client.delete_treatment(treatment["id"])
    inactive_response, active_response = await asyncio.gather(
        medisolveai_admin_client.get_treatments(is_active=False),
        medisolveai_admin_client.get_treatments(is_active=True),
    )

    # Then: 응답 코드 확인 (204) 및 필터 검증
    assert delete_response.status_code == 204
    inactive_items = inactive_response.json()
    assert any(item["id"] == treatment["id"] for item in inactive_items)
    active_items = active_response.json()
    assert all(item["id"] != treatment["id"] for item in active_items)


async def test_delete_treatment_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 진료 항목 비활성화 시 예외"""

    # When: 존재하지 않는 ID로 비활성화 시도
    response = await medisolveai_admin_client.delete_treatment(9999)

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.TREATMENT_NOT_FOUND


async def test_get_treatments_pagination(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """진료 항목 목록 조회 - 페이지네이션"""

    treatment_mother = TreatmentMother(medisolveai_admin_client)

    # Given: 총 12개의 진료 항목 생성
    await treatment_mother.create_bulk(count=12, base_name="Treatment", duration_minutes=30, price="10000.00")

    # When: 첫 페이지 조회
    page1_response = await medisolveai_admin_client.get_treatments()

    # Then: 첫 페이지 결과 검증
    assert page1_response.status_code == 200
    page1_items = page1_response.json()
    assert len(page1_items) == 10
    assert page1_items[0]["name"] == "Treatment 0"
    assert page1_items[-1]["name"] == "Treatment 9"

    # When: 두 번째 페이지 조회
    page2_response = await medisolveai_admin_client.get_treatments(page=2)

    # Then: 두 번째 페이지 결과 검증
    assert page2_response.status_code == 200
    page2_items = page2_response.json()
    assert len(page2_items) == 2
    assert page2_items[0]["name"] == "Treatment 10"
    assert page2_items[1]["name"] == "Treatment 11"
