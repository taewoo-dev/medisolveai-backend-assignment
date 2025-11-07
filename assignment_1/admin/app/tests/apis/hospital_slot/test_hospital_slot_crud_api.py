"""Hospital Slot CRUD API 테스트"""

from __future__ import annotations

import asyncio

from app.core.constants import ErrorMessages
from app.tests.mothers import HospitalSlotMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_create_hospital_slot_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """병원 시간대 생성 성공"""

    # When: 병원 슬롯 생성
    response = await medisolveai_admin_client.create_hospital_slot(
        start_time="09:00",
        end_time="09:30",
        max_capacity=3,
    )

    # Then: 생성 결과 검증
    assert response.status_code == 201
    slot = response.json()
    assert slot["start_time"] == "09:00:00"
    assert slot["end_time"] == "09:30:00"
    assert slot["max_capacity"] == 3
    assert slot["is_active"] is True


async def test_create_hospital_slot_invalid_interval(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """30분 간격이 아니면 생성 실패"""

    # When: 30분 간격이 아닌 시간대 생성 시도
    response = await medisolveai_admin_client.create_hospital_slot(
        start_time="09:10",
        end_time="09:40",
        max_capacity=2,
    )

    # Then: 검증 실패 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.HOSPITAL_SLOT_INVALID_INTERVAL


async def test_create_hospital_slot_conflict(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """동일 시간대 생성 시 충돌"""

    mother = HospitalSlotMother(medisolveai_admin_client)

    # Given: 기존 슬롯 생성
    await mother.create(start_time="10:00", end_time="10:30", max_capacity=2)

    # When: 동일 시간대 슬롯 생성 시도
    response = await medisolveai_admin_client.create_hospital_slot(
        start_time="10:00",
        end_time="10:30",
        max_capacity=5,
    )

    # Then: 충돌 에러 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.HOSPITAL_SLOT_TIME_CONFLICT


async def test_get_hospital_slots_filtered(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """활성 여부 필터링 조회"""

    mother = HospitalSlotMother(medisolveai_admin_client)

    # Given: 활성 및 비활성 슬롯 생성
    await asyncio.gather(
        mother.create(start_time="09:00", end_time="09:30", is_active=True),
        mother.create(start_time="09:30", end_time="10:00", is_active=False),
    )

    # When: 활성 슬롯만 조회
    active_response, inactive_response = await asyncio.gather(
        medisolveai_admin_client.get_hospital_slots(is_active=True),
        medisolveai_admin_client.get_hospital_slots(is_active=False),
    )

    # Then: 활성 슬롯 확인
    assert active_response.status_code == 200
    active_slots = active_response.json()
    assert len(active_slots) == 1
    assert active_slots[0]["is_active"] is True

    # Then: 비활성 슬롯 확인
    assert inactive_response.status_code == 200
    inactive_slots = inactive_response.json()
    assert len(inactive_slots) == 1
    assert inactive_slots[0]["is_active"] is False


async def test_update_hospital_slot_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """병원 시간대 수정 성공"""

    mother = HospitalSlotMother(medisolveai_admin_client)

    # Given: 기존 슬롯 생성
    slot = await mother.create(start_time="11:00", end_time="11:30", max_capacity=3)

    # When: 최대 수용 인원 수정
    response = await medisolveai_admin_client.update_hospital_slot(
        slot["id"],
        max_capacity=5,
    )

    # Then: 수정 결과 검증
    assert response.status_code == 200
    updated_slot = response.json()
    assert updated_slot["start_time"] == "11:00:00"
    assert updated_slot["end_time"] == "11:30:00"
    assert updated_slot["max_capacity"] == 5


async def test_update_hospital_slot_time_change_not_allowed(
    medisolveai_admin_client: MediSolveAiAdminClient,
) -> None:
    """시간대 수정 시도 시 422 응답"""

    mother = HospitalSlotMother(medisolveai_admin_client)

    # Given: 기존 슬롯 생성
    slot = await mother.create(start_time="13:00", end_time="13:30")

    # When: 시간대 변경 + 수용 인원 수정 시도
    response = await medisolveai_admin_client.update_hospital_slot(
        slot["id"],
        start_time="13:30",
        end_time="14:00",
        max_capacity=4,
    )

    # Then: 유효성 오류 확인
    assert response.status_code == 422


async def test_update_hospital_slot_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 슬롯 수정 시 예외"""

    # When: 존재하지 않는 슬롯에 대한 수정 시도
    response = await medisolveai_admin_client.update_hospital_slot(9999, max_capacity=10)

    # Then: 오류 메시지 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.HOSPITAL_SLOT_NOT_FOUND


async def test_delete_hospital_slot_success(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """병원 시간대 비활성화 성공"""

    mother = HospitalSlotMother(medisolveai_admin_client)

    # Given: 기존 슬롯 생성
    slot = await mother.create(start_time="15:00", end_time="15:30")

    # When: 슬롯 비활성화 후 비활성/활성 목록 조회
    delete_response = await medisolveai_admin_client.delete_hospital_slot(slot["id"])
    inactive_response, active_response = await asyncio.gather(
        medisolveai_admin_client.get_hospital_slots(is_active=False),
        medisolveai_admin_client.get_hospital_slots(is_active=True),
    )

    # Then: 비활성화 확인
    assert delete_response.status_code == 204
    inactive_slots = inactive_response.json()
    assert any(item["id"] == slot["id"] for item in inactive_slots)
    active_slots = active_response.json()
    assert all(item["id"] != slot["id"] for item in active_slots)


async def test_delete_hospital_slot_not_found(medisolveai_admin_client: MediSolveAiAdminClient) -> None:
    """존재하지 않는 슬롯 삭제 시 예외"""

    # When: 존재하지 않는 슬롯 비활성화 시도
    response = await medisolveai_admin_client.delete_hospital_slot(9999)

    # Then: 오류 메시지 확인
    assert response.status_code == 400
    error = response.json()
    assert error["message"] == ErrorMessages.HOSPITAL_SLOT_NOT_FOUND
