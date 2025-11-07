"""Admin Appointment List API 테스트"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import AppointmentStatus, VisitType
from app.tests.mothers import AppointmentMother, DoctorMother, TreatmentMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_get_appointments_success(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 목록 조회 - 페이지네이션"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    # Given: 예약 3건 생성 (최근 순)
    doctor, treatment = await asyncio.gather(
        doctor_mother.create(name="Dr. Kim"),
        treatment_mother.create(name="레이저 시술", duration_minutes=30),
    )

    await appointment_mother.create(
        doctor_id=doctor["id"],
        treatment_id=treatment["id"],
        appointment_datetime=(base_datetime := datetime(2025, 1, 10, 10, 0)),
        status=AppointmentStatus.CONFIRMED,
        visit_type=VisitType.FIRST_VISIT,
        patient_name="홍길동",
        patient_phone="010-1234-5678",
    )

    await asyncio.gather(
        *[
            appointment_mother.create(
                doctor_id=doctor["id"],
                treatment_id=treatment["id"],
                appointment_datetime=base_datetime - timedelta(hours=idx),
                status=AppointmentStatus.CONFIRMED,
                visit_type=VisitType.FIRST_VISIT,
                patient_name="홍길동",
                patient_phone="010-1234-5678",
            )
            for idx in (1, 2)
        ]
    )

    # When: 예약 목록 1, 2페이지 조회 (동시 실행)
    response_page1, response_page2 = await asyncio.gather(
        medisolveai_admin_client.get_appointments(page=1, page_size=2),
        medisolveai_admin_client.get_appointments(page=2, page_size=2),
    )

    # Then: 페이지네이션 결과 검증
    assert response_page1.status_code == 200
    assert response_page2.status_code == 200

    page1 = response_page1.json()
    page2 = response_page2.json()

    assert page1["total_count"] == 3
    assert page1["total_pages"] == 2
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 1

    first_item = page1["items"][0]
    assert first_item["appointment_datetime"].startswith("2025-01-10T10:00:00")
    assert first_item["doctor_id"] == doctor["id"]
    assert first_item["treatment_id"] == treatment["id"]


async def test_get_appointments_filters(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 목록 조회 - 필터 적용"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    # Given: 서로 다른 조건의 예약 생성
    (doctor_a, doctor_b), (treatment_a, treatment_b) = await asyncio.gather(
        asyncio.gather(
            doctor_mother.create(name="Dr. Ahn"),
            doctor_mother.create(name="Dr. Bae"),
        ),
        asyncio.gather(
            treatment_mother.create(name="IPL", duration_minutes=30),
            treatment_mother.create(name="필러", duration_minutes=60),
        ),
    )

    await asyncio.gather(
        appointment_mother.create(
            doctor_id=doctor_a["id"],
            treatment_id=treatment_a["id"],
            appointment_datetime=datetime(2025, 1, 15, 14, 0),
            status=AppointmentStatus.CONFIRMED,
            visit_type=VisitType.FIRST_VISIT,
            patient_name="김철수",
            patient_phone="010-1111-2222",
        ),
        appointment_mother.create(
            doctor_id=doctor_b["id"],
            treatment_id=treatment_a["id"],
            appointment_datetime=datetime(2025, 1, 16, 9, 0),
            status=AppointmentStatus.PENDING,
            visit_type=VisitType.RETURN_VISIT,
            patient_name="이영희",
            patient_phone="010-3333-4444",
        ),
        appointment_mother.create(
            doctor_id=doctor_b["id"],
            treatment_id=treatment_b["id"],
            appointment_datetime=datetime(2025, 1, 20, 11, 30),
            status=AppointmentStatus.CANCELLED,
            visit_type=VisitType.RETURN_VISIT,
            patient_name="박민수",
            patient_phone="010-5555-6666",
        ),
    )

    # When: 상태, 의사, 기간 필터 조회 (동시 실행)
    response_status, response_doctor, response_date = await asyncio.gather(
        medisolveai_admin_client.get_appointments(
            status=AppointmentStatus.CONFIRMED.value,
            page=1,
            page_size=10,
        ),
        medisolveai_admin_client.get_appointments(
            doctor_id=doctor_b["id"],
            page=1,
            page_size=10,
        ),
        medisolveai_admin_client.get_appointments(
            start_date=date(2025, 1, 16).isoformat(),
            end_date=date(2025, 1, 16).isoformat(),
            page=1,
            page_size=10,
        ),
    )

    # Then: 필터 결과 검증
    assert response_status.status_code == 200
    status_items = response_status.json()["items"]
    assert len(status_items) == 1
    assert status_items[0]["status"] == AppointmentStatus.CONFIRMED.value

    assert response_doctor.status_code == 200
    doctor_items = response_doctor.json()["items"]
    assert len(doctor_items) == 2
    assert {item["doctor_id"] for item in doctor_items} == {doctor_b["id"]}

    assert response_date.status_code == 200
    date_items = response_date.json()["items"]
    assert len(date_items) == 1
    assert date_items[0]["appointment_datetime"].startswith("2025-01-16T09:00:00")


async def test_get_appointments_invalid_page_size(
    medisolveai_admin_client: MediSolveAiAdminClient,
) -> None:
    """예약 목록 조회 - 페이지 크기 초과 시 422"""

    # When: 허용 범위를 벗어난 페이지 크기로 조회
    response = await medisolveai_admin_client.get_appointments(page=1, page_size=0)

    # Then: 검증 실패 확인
    assert response.status_code == 422
