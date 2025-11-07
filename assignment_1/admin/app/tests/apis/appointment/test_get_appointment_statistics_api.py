"""Admin Appointment Statistics API 테스트"""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import AppointmentStatus, VisitType
from app.tests.mothers import AppointmentMother, DoctorMother, TreatmentMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_get_appointment_statistics_success(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 통계 조회 성공"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    # Given: 동일한 의사/진료 항목으로 다양한 상태/시간대의 예약 생성
    doctor, treatment = await asyncio.gather(
        doctor_mother.create(name="Dr. Stat"),
        treatment_mother.create(name="필러", duration_minutes=30),
    )

    await asyncio.gather(
        appointment_mother.create(
            doctor_id=doctor["id"],
            treatment_id=treatment["id"],
            appointment_datetime=datetime(2025, 3, 1, 10, 0),
            status=AppointmentStatus.CONFIRMED,
            visit_type=VisitType.FIRST_VISIT,
            patient_name="통계1",
            patient_phone="010-8000-0001",
        ),
        appointment_mother.create(
            doctor_id=doctor["id"],
            treatment_id=treatment["id"],
            appointment_datetime=datetime(2025, 3, 1, 14, 0),
            status=AppointmentStatus.PENDING,
            visit_type=VisitType.RETURN_VISIT,
            patient_name="통계2",
            patient_phone="010-8000-0002",
        ),
        appointment_mother.create(
            doctor_id=doctor["id"],
            treatment_id=treatment["id"],
            appointment_datetime=datetime(2025, 3, 2, 9, 30),
            status=AppointmentStatus.CANCELLED,
            visit_type=VisitType.FIRST_VISIT,
            patient_name="통계3",
            patient_phone="010-8000-0003",
        ),
    )

    # When: 3월 1~2일에 대한 통계 조회
    response = await medisolveai_admin_client.get_appointment_statistics(
        start_date="2025-03-01",
        end_date="2025-03-02",
    )

    # Then: 상태/일별/시간대/방문 유형별 건수가 올바른지 검증
    assert response.status_code == 200
    stats = response.json()

    status_counts = {item["status"]: item["count"] for item in stats["status_counts"]}
    assert status_counts[AppointmentStatus.CONFIRMED.value] == 1
    assert status_counts[AppointmentStatus.PENDING.value] == 1
    assert status_counts[AppointmentStatus.CANCELLED.value] == 1

    daily_counts = {item["day"]: item["count"] for item in stats["daily_counts"]}
    assert daily_counts["2025-03-01"] == 2
    assert daily_counts["2025-03-02"] == 1

    timeslot_counts = {item["hour"]: item["count"] for item in stats["timeslot_counts"]}
    assert timeslot_counts[10] == 1
    assert timeslot_counts[14] == 1
    assert timeslot_counts[9] == 1

    visit_counts = {item["visit_type"]: item["count"] for item in stats["visit_type_counts"]}
    assert visit_counts[VisitType.FIRST_VISIT.value] == 2
    assert visit_counts[VisitType.RETURN_VISIT.value] == 1


async def test_get_appointment_statistics_with_filters(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 통계 조회 - 필터 적용"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    # Given: 서로 다른 의사로 동일 날짜 예약 생성
    doctor_a, doctor_b = await asyncio.gather(
        doctor_mother.create(name="Dr. Filter A"),
        doctor_mother.create(name="Dr. Filter B"),
    )
    treatment = await treatment_mother.create(name="레이저", duration_minutes=30)

    await asyncio.gather(
        appointment_mother.create(
            doctor_id=doctor_a["id"],
            treatment_id=treatment["id"],
            appointment_datetime=datetime(2025, 4, 1, 11, 0),
            status=AppointmentStatus.CONFIRMED,
            patient_name="필터1",
            patient_phone="010-7000-0001",
        ),
        appointment_mother.create(
            doctor_id=doctor_b["id"],
            treatment_id=treatment["id"],
            appointment_datetime=datetime(2025, 4, 1, 15, 0),
            status=AppointmentStatus.CONFIRMED,
            patient_name="필터2",
            patient_phone="010-7000-0002",
        ),
    )

    # When: 특정 의사 ID를 기준으로 통계 조회
    response = await medisolveai_admin_client.get_appointment_statistics(
        start_date="2025-04-01",
        end_date="2025-04-01",
        doctor_id=doctor_a["id"],
    )

    # Then: 해당 의사의 예약만 집계되는지 확인
    assert response.status_code == 200
    stats = response.json()

    daily_counts = {item["day"]: item["count"] for item in stats["daily_counts"]}
    assert daily_counts["2025-04-01"] == 1

    status_counts = {item["status"]: item["count"] for item in stats["status_counts"]}
    assert status_counts[AppointmentStatus.CONFIRMED.value] == 1
