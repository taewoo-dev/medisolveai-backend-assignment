"""Admin Appointment Status Update API 테스트"""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import AppointmentStatus
from app.tests.mothers import AppointmentMother, DoctorMother, TreatmentMother
from app.tests.test_client import MediSolveAiAdminClient


async def test_update_appointment_status_success(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 상태 변경 성공"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    doctor, treatment = await asyncio.gather(
        doctor_mother.create(name="Dr. Status"),
        treatment_mother.create(name="레이저", duration_minutes=30),
    )

    appointment = await appointment_mother.create(
        doctor_id=doctor["id"],
        treatment_id=treatment["id"],
        appointment_datetime=datetime(2025, 1, 21, 11, 0),
        status=AppointmentStatus.PENDING,
        patient_name="상태 테스트",
        patient_phone="010-9000-0001",
    )

    response = await medisolveai_admin_client.update_appointment_status(
        appointment_id=appointment["id"],
        status=AppointmentStatus.CONFIRMED.value,
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == AppointmentStatus.CONFIRMED.value

    list_response = await medisolveai_admin_client.get_appointments(status=AppointmentStatus.CONFIRMED.value)
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert any(item["id"] == appointment["id"] for item in items)


async def test_update_appointment_status_invalid_transition(
    medisolveai_admin_client: MediSolveAiAdminClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """허용되지 않는 예약 상태 변경 시 실패"""

    doctor_mother = DoctorMother(medisolveai_admin_client)
    treatment_mother = TreatmentMother(medisolveai_admin_client)
    appointment_mother = AppointmentMother(session_maker_medisolveai)

    doctor, treatment = await asyncio.gather(
        doctor_mother.create(name="Dr. Final"),
        treatment_mother.create(name="필러", duration_minutes=30),
    )

    appointment = await appointment_mother.create(
        doctor_id=doctor["id"],
        treatment_id=treatment["id"],
        appointment_datetime=datetime(2025, 2, 1, 14, 30),
        status=AppointmentStatus.COMPLETED,
        patient_name="완료 환자",
        patient_phone="010-9000-0002",
    )

    response = await medisolveai_admin_client.update_appointment_status(
        appointment_id=appointment["id"],
        status=AppointmentStatus.PENDING.value,
    )

    assert response.status_code == 400
    assert response.json()["message"] == "해당 예약 상태로 변경할 수 없습니다."
